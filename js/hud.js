/* FRANK scroll HUD: one WebGL stage that morphs through the page, a HUD that
   reads the page back, and the approval gate demo. No dependencies. */

(function(){
"use strict";
var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
setTimeout(function(){ document.documentElement.classList.remove('booting'); }, reduce?0:2200);

/* ═══ 1. WEBGL STAGE ══════════════════════════════════ */
var cv = document.getElementById('stage');
var bloomEl = document.getElementById('bloom');
var gl = cv.getContext('webgl', {alpha:true, antialias:true, premultipliedAlpha:false});

function ident(){return new Float32Array([1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]);}
function persp(fov,a,n,f){var t=1/Math.tan(fov/2),o=ident();
  o[0]=t/a;o[5]=t;o[10]=(f+n)/(n-f);o[11]=-1;o[14]=2*f*n/(n-f);o[15]=0;return o;}
function mul(a,b){var o=new Float32Array(16);
  for(var i=0;i<4;i++)for(var j=0;j<4;j++){var s=0;
    for(var k=0;k<4;k++)s+=a[k*4+j]*b[i*4+k]; o[i*4+j]=s;} return o;}
function trans(x,y,z){var o=ident();o[12]=x;o[13]=y;o[14]=z;return o;}
function rotY(r){var o=ident(),c=Math.cos(r),s=Math.sin(r);o[0]=c;o[2]=-s;o[8]=s;o[10]=c;return o;}
function rotX(r){var o=ident(),c=Math.cos(r),s=Math.sin(r);o[5]=c;o[6]=s;o[9]=-s;o[10]=c;return o;}

function icosphere(sub){
  var t=(1+Math.sqrt(5))/2;
  var v=[[-1,t,0],[1,t,0],[-1,-t,0],[1,-t,0],[0,-1,t],[0,1,t],
         [0,-1,-t],[0,1,-t],[t,0,-1],[t,0,1],[-t,0,-1],[-t,0,1]];
  var f=[[0,11,5],[0,5,1],[0,1,7],[0,7,10],[0,10,11],[1,5,9],[5,11,4],[11,10,2],
         [10,7,6],[7,1,8],[3,9,4],[3,4,2],[3,2,6],[3,6,8],[3,8,9],[4,9,5],
         [2,4,11],[6,2,10],[8,6,7],[9,8,1]];
  var norm=function(p){var l=Math.hypot(p[0],p[1],p[2]);return [p[0]/l,p[1]/l,p[2]/l];};
  v=v.map(norm);
  for(var s=0;s<sub;s++){
    var cache={}, nf=[];
    var mid=function(a,b){
      var k=a<b?a+'_'+b:b+'_'+a;
      if(cache[k]!==undefined)return cache[k];
      var p=norm([(v[a][0]+v[b][0])/2,(v[a][1]+v[b][1])/2,(v[a][2]+v[b][2])/2]);
      v.push(p); return (cache[k]=v.length-1);
    };
    for(var i=0;i<f.length;i++){
      var a=f[i][0],b=f[i][1],c=f[i][2];
      var ab=mid(a,b), bc=mid(b,c), ca=mid(c,a);
      nf.push([a,ab,ca],[b,bc,ab],[c,ca,bc],[ab,bc,ca]);
    }
    f=nf;
  }
  var seen={}, idx=[];
  for(var j=0;j<f.length;j++){
    var tri=f[j];
    for(var e=0;e<3;e++){
      var p1=tri[e], p2=tri[(e+1)%3];
      var key=p1<p2?p1+'_'+p2:p2+'_'+p1;
      if(!seen[key]){seen[key]=1; idx.push(p1,p2);}
    }
  }
  var flat=new Float32Array(v.length*3), tor=new Float32Array(v.length*3);
  for(var q=0;q<v.length;q++){
    var x=v[q][0], y=v[q][1], z=v[q][2];
    flat[q*3]=x; flat[q*3+1]=y; flat[q*3+2]=z;
    /* morph target: a woven torus — same topology, different form */
    var th=Math.atan2(z,x), ph=Math.asin(Math.max(-1,Math.min(1,y)))*2.0;
    var R=1.62, r=0.34;
    tor[q*3]  =(R + r*Math.cos(ph))*Math.cos(th);
    tor[q*3+1]= r*Math.sin(ph);
    tor[q*3+2]=(R + r*Math.cos(ph))*Math.sin(th);
  }
  return {pos:flat, tor:tor, idx:new Uint16Array(idx), n:v.length};
}

var VS = [
'attribute vec3 aPos;',
'attribute vec3 aPos2;',
'uniform mat4 uProj, uMV;',
'uniform float uTime, uAmp, uFlat, uScale, uPt, uMorph, uStream;',
'varying float vD; varying float vN;',
'float hash(vec3 p){ return fract(sin(dot(p, vec3(12.9898,78.233,45.164)))*43758.5453); }',
'void main(){',
'  vec3 target = aPos2;',
'  if(uStream > 0.5){',
'    float sd = hash(aPos);',
'    float t = fract(sd + uTime*0.055);',
'    target = vec3(mix(-4.6,4.6,t), (sd-0.5)*1.45, (fract(sd*7.13)-0.5)*1.45);',
'  }',
'  vec3 base = mix(aPos, target, uMorph);',
'  vec3 d = normalize(base + vec3(0.0001));',
'  float n = sin(base.x*2.7+uTime*.62)*sin(base.y*2.4-uTime*.47)*sin(base.z*2.9+uTime*.55);',
'  vec3 p = base + d*n*uAmp;',
'  p.z *= (1.0 - uFlat*0.93);',
'  p.xy *= (1.0 + uFlat*0.30);',
'  p *= uScale;',
'  vec4 mv = uMV * vec4(p,1.0);',
'  vD = -mv.z; vN = 0.5+0.5*n;',
'  gl_PointSize = uPt;',
'  gl_Position = uProj * mv;',
'}'].join('\n');

var FS = [
'precision mediump float;',
'varying float vD; varying float vN;',
'uniform float uOp; uniform vec3 uA, uB;',
'void main(){',
'  float d = clamp((vD-2.2)/6.2, 0.0, 1.0);',
'  vec3 c = mix(uA, uB, clamp(d*1.05 + vN*0.22, 0.0, 1.0));',
'  float a = (1.0 - d*0.88) * uOp;',
'  gl_FragColor = vec4(c, a);',
'}'].join('\n');

var prog, uni={}, sph, sphBuf, torBuf, sphIdx, ptBuf, ptCount=0, ok=!!gl;
var aPosLoc=0, aPos2Loc=0;

function sh(type,src){var s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);
  if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)){ok=false;} return s;}

if(ok){
  prog=gl.createProgram();
  gl.attachShader(prog,sh(gl.VERTEX_SHADER,VS));
  gl.attachShader(prog,sh(gl.FRAGMENT_SHADER,FS));
  gl.linkProgram(prog);
  if(!gl.getProgramParameter(prog,gl.LINK_STATUS)) ok=false;
}
if(ok){
  gl.useProgram(prog);
  ['uProj','uMV','uTime','uAmp','uFlat','uScale','uOp','uA','uB','uPt','uMorph','uStream']
    .forEach(function(k){ uni[k]=gl.getUniformLocation(prog,k); });
  aPosLoc  = gl.getAttribLocation(prog,'aPos');
  aPos2Loc = gl.getAttribLocation(prog,'aPos2');

  sph = icosphere(3);
  sphBuf=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,sphBuf);
  gl.bufferData(gl.ARRAY_BUFFER,sph.pos,gl.STATIC_DRAW);
  torBuf=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,torBuf);
  gl.bufferData(gl.ARRAY_BUFFER,sph.tor,gl.STATIC_DRAW);
  sphIdx=gl.createBuffer(); gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,sphIdx);
  gl.bufferData(gl.ELEMENT_ARRAY_BUFFER,sph.idx,gl.STATIC_DRAW);

  ptCount=820;
  var pts=new Float32Array(ptCount*3);
  for(var i=0;i<ptCount;i++){
    var th=Math.random()*Math.PI*2, ph=Math.acos(2*Math.random()-1);
    var r=1.45+Math.random()*1.55;
    pts[i*3]  =r*Math.sin(ph)*Math.cos(th);
    pts[i*3+1]=r*Math.sin(ph)*Math.sin(th)*0.72;
    pts[i*3+2]=r*Math.cos(ph);
  }
  ptBuf=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,ptBuf);
  gl.bufferData(gl.ARRAY_BUFFER,pts,gl.STATIC_DRAW);

  gl.enableVertexAttribArray(aPosLoc);
  gl.enableVertexAttribArray(aPos2Loc);
  gl.enable(gl.BLEND);
  gl.blendFunc(gl.SRC_ALPHA, gl.ONE);
  gl.disable(gl.DEPTH_TEST);
}

var W=0,H=0,DPR=1;
function resize(){
  DPR=Math.min(devicePixelRatio||1, 2);
  W=innerWidth; H=innerHeight;
  cv.width=W*DPR; cv.height=H*DPR; cv.style.width=W+'px'; cv.style.height=H+'px';
  if(ok) gl.viewport(0,0,cv.width,cv.height);
}
addEventListener('resize',resize,{passive:true});
resize();

/* one stage, seven beats — mix: sphere→torus, stream: shell→pipeline */
var KEY=[
  {at:0.00, sc:0.84, ox:2.30, oy:0.18, amp:0.12, flat:0.00, op:1.00, spin:0.16, tilt:0.10, mix:0.00, str:0.00},
  {at:0.18, sc:0.54, ox:3.10, oy:0.40, amp:0.26, flat:0.04, op:0.62, spin:0.34, tilt:-0.16,mix:0.00, str:0.92},
  {at:0.36, sc:0.94, ox:0.00, oy:-0.90,amp:0.09, flat:0.64, op:0.86, spin:0.46, tilt:0.54, mix:0.18, str:0.10},
  {at:0.54, sc:0.62, ox:3.00, oy:0.22, amp:0.14, flat:0.20, op:0.60, spin:0.30, tilt:0.20, mix:0.35, str:0.35},
  {at:0.72, sc:1.00, ox:2.05, oy:0.05, amp:0.06, flat:0.10, op:1.00, spin:0.58, tilt:0.62, mix:1.00, str:0.00},
  {at:0.87, sc:0.66, ox:-2.60,oy:0.10, amp:0.10, flat:0.30, op:0.52, spin:0.26, tilt:0.30, mix:0.55, str:0.25},
  {at:1.00, sc:1.34, ox:0.00, oy:-0.20,amp:0.16, flat:0.18, op:0.52, spin:0.20, tilt:0.14, mix:0.10, str:0.15}
];
var LERPK=['sc','ox','oy','amp','flat','op','spin','tilt','mix','str'];
function lerpKey(p){
  var a=KEY[0], b=KEY[KEY.length-1];
  for(var i=0;i<KEY.length-1;i++){ if(p>=KEY[i].at && p<=KEY[i+1].at){a=KEY[i];b=KEY[i+1];break;} }
  var span=(b.at-a.at)||1, t=Math.min(1,Math.max(0,(p-a.at)/span));
  t = t*t*(3-2*t);
  var o={};
  for(var j=0;j<LERPK.length;j++){var k=LERPK[j]; o[k]=a[k]+(b[k]-a[k])*t;}
  return o;
}

var prog01=0, tgt01=0, spin=0, t0=performance.now(), frames=0, fpsT=t0;
var fpsEl=document.getElementById('hudFps');

function draw(now){
  requestAnimationFrame(draw);
  if(!ok) return;
  var dt=Math.min(0.05,(now-t0)/1000); t0=now;
  prog01 += (tgt01-prog01)*0.08;
  var k=lerpKey(prog01);
  var time=now/1000;
  spin += dt*(reduce?0.02:k.spin);

  frames++;
  if(now-fpsT>620){ if(fpsEl) fpsEl.textContent=Math.round(frames*1000/(now-fpsT))+' fps';
    frames=0; fpsT=now; }

  gl.clearColor(0,0,0,0); gl.clear(gl.COLOR_BUFFER_BIT);

  var aspect=W/H;
  var P=persp(1.05, aspect, 0.1, 60);
  /* portrait: the core has nowhere to sit beside the copy, so it recedes */
  var portrait = aspect<1.05;
  var xShift = portrait ? 0 : k.ox;
  var scMul  = portrait ? 0.64 : 1.0;
  var opMul  = portrait ? 0.46 : 1.0;
  var MV = mul(trans(xShift, k.oy, -5.4), mul(rotY(spin), rotX(k.tilt)));

  if(bloomEl){
    var ppu=(H/2)/3.138;
    bloomEl.style.setProperty('--bx',(xShift*ppu).toFixed(0)+'px');
    bloomEl.style.setProperty('--by',(-k.oy*ppu).toFixed(0)+'px');
    bloomEl.style.setProperty('--bo',(k.op*0.95*opMul).toFixed(2));
  }

  gl.uniformMatrix4fv(uni.uProj,false,P);
  gl.uniformMatrix4fv(uni.uMV,false,MV);
  gl.uniform1f(uni.uTime, reduce?0:time);
  gl.uniform1f(uni.uFlat, k.flat);
  gl.uniform3f(uni.uA, 0.078,0.722,0.651);
  gl.uniform3f(uni.uB, 0.055,0.647,0.914);

  /* wireframe: sphere morphing to torus */
  gl.bindBuffer(gl.ARRAY_BUFFER,sphBuf);
  gl.vertexAttribPointer(aPosLoc,3,gl.FLOAT,false,0,0);
  gl.bindBuffer(gl.ARRAY_BUFFER,torBuf);
  gl.vertexAttribPointer(aPos2Loc,3,gl.FLOAT,false,0,0);
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,sphIdx);
  gl.uniform1f(uni.uMorph, k.mix);
  gl.uniform1f(uni.uStream, 0.0);
  gl.uniform1f(uni.uAmp, k.amp);
  gl.uniform1f(uni.uScale, k.sc*1.55*scMul);
  gl.uniform1f(uni.uOp, k.op*0.80*opMul);
  gl.uniform1f(uni.uPt, 1.0);
  gl.drawElements(gl.LINES, sph.idx.length, gl.UNSIGNED_SHORT, 0);

  /* particles: shell dissolving into a left-to-right work stream */
  gl.bindBuffer(gl.ARRAY_BUFFER,ptBuf);
  gl.vertexAttribPointer(aPosLoc,3,gl.FLOAT,false,0,0);
  gl.vertexAttribPointer(aPos2Loc,3,gl.FLOAT,false,0,0);
  gl.uniform1f(uni.uMorph, k.str);
  gl.uniform1f(uni.uStream, 1.0);
  gl.uniform1f(uni.uAmp, k.amp*1.8);
  gl.uniform1f(uni.uScale, k.sc*1.9*scMul);
  gl.uniform1f(uni.uOp, k.op*opMul);
  gl.uniform1f(uni.uPt, 1.9*DPR);
  gl.drawArrays(gl.POINTS, 0, ptCount);
}
requestAnimationFrame(draw);

/* ═══ 2. HUD ══════════════════════════════════════════ */
var $=function(id){return document.getElementById(id);};
var logEl=$('hudLog'), secEl=$('hudSec'), depthEl=$('hudDepth'), pctEl=$('hudPct');
var ringEl=$('hudRing'), stateEl=$('hudState'), queueEl=$('hudQueue'), clockEl=$('hudClock');
var mNow=$('mNow'), mBar=$('mBar'), mPct=$('mPct');
var held=$('hudHeld'), heldTxt=$('hudHeldTxt');
var dock=$('dock'), dockIdx=$('dockIdx'), dockTitle=$('dockTitle'), dockRead=$('dockRead');
var CIRC=175.9;
var sections=[].slice.call(document.querySelectorAll('section[data-sec]'));
var current=null, currentIdx=0;

function pushLog(text, warn){
  var li=document.createElement('li');
  if(warn) li.className='warn';
  li.innerHTML='<b>&gt;</b> '+text;
  logEl.appendChild(li);
  while(logEl.children.length>5) logEl.removeChild(logEl.firstChild);
}
function clock(){
  var d=new Date();
  clockEl.textContent=String(d.getHours()).padStart(2,'0')+':'+String(d.getMinutes()).padStart(2,'0');
}
clock(); setInterval(clock,20000);

var boot=['core online','operator profile loaded','3 systems indexed','approval gate armed'];
if(reduce){ boot.forEach(function(b){pushLog(b);}); stateEl.textContent='online'; }
else {
  boot.forEach(function(b,i){ setTimeout(function(){
    pushLog(b);
    if(i===boot.length-1) stateEl.textContent='online';
  }, 900+i*380); });
}

/* the dock physically slides to meet the active section's heading */
function placeDock(){
  if(!current) return;
  var h=current.querySelector('h1,h2');
  if(!h) return;
  var r=h.getBoundingClientRect();
  var top=Math.min(Math.max(r.top + r.height/2 - 42, 150), innerHeight-260);
  dock.style.top=top+'px';
}

var ticking=false;
function onScroll(){
  if(ticking) return; ticking=true;
  requestAnimationFrame(function(){
    ticking=false;
    var max=document.documentElement.scrollHeight-innerHeight;
    var p=max>0 ? Math.min(1,Math.max(0,scrollY/max)) : 0;
    tgt01=p;
    var pc=Math.round(p*100);
    depthEl.textContent=p.toFixed(2);
    pctEl.textContent=pc+'%';
    ringEl.style.strokeDashoffset=(CIRC*(1-p)).toFixed(1);
    mBar.style.width=pc+'%'; mPct.textContent=pc+'%';
    placeDock();
  });
}
addEventListener('scroll',onScroll,{passive:true});
addEventListener('resize',onScroll,{passive:true});

var io=new IntersectionObserver(function(entries){
  entries.forEach(function(en){
    if(!en.isIntersecting) return;
    var s=en.target;
    if(s===current) return;
    current=s; currentIdx=sections.indexOf(s);

    var name=s.getAttribute('data-sec')||'—';
    secEl.textContent=name;
    mNow.textContent='FRANK · '+name.toLowerCase();

    dockIdx.textContent=String(currentIdx+1).padStart(2,'0')+' / '+String(sections.length).padStart(2,'0');
    dockTitle.textContent=s.getAttribute('data-title')||name;
    dockRead.textContent=s.getAttribute('data-read')||'';
    placeDock();

    var lines=(s.getAttribute('data-log')||'').split('|').filter(Boolean);
    var warn=s.getAttribute('data-warn')==='1';
    lines.forEach(function(l,i){
      setTimeout(function(){ pushLog(l, warn); }, reduce?0:i*300);
    });
    if(s.id==='gate') setHeld(true);
  });
},{threshold:0.42});
sections.forEach(function(s){io.observe(s);});
onScroll();

/* section reveals */
var rio=new IntersectionObserver(function(entries){
  entries.forEach(function(en){
    if(en.isIntersecting){ en.target.classList.add('in'); rio.unobserve(en.target); }
  });
},{threshold:0.12, rootMargin:'0px 0px -6% 0px'});
var rvAll=[].slice.call(document.querySelectorAll('.rv'));
rvAll.forEach(function(el,i){
  el.style.transitionDelay=(Math.min(i%6,5)*0.06)+'s';
  rio.observe(el);
});
/* nothing stays invisible: anything still unrevealed after 4s is shown regardless */
setTimeout(function(){ rvAll.forEach(function(el){ el.classList.add('in'); }); }, 4000);

/* ═══ 3. APPROVAL GATE (the real mechanic) ════════════ */
var approved=false;
function setHeld(on){
  if(approved) return;
  held.classList.toggle('on', !!on);
  queueEl.textContent = on ? '1 held' : '0 held';
}
function approve(){
  if(approved) return;
  approved=true;
  held.classList.add('cleared');
  heldTxt.innerHTML='RELEASED<br>approved by operator';
  $('hudApprove').textContent='DONE';
  queueEl.textContent='0 held';

  var q=$('q1');
  q.classList.add('done');
  $('q1tag').textContent='APPROVED';
  $('q1p').textContent='Released to the scheduler. Publishes Thursday 7:30pm.';
  $('q1act').textContent='✓ RELEASED BY YOU';
  var st=$('gateSt');
  st.innerHTML='<i style="background:#14B8A6"></i> QUEUE CLEAR';
  st.style.color='#14B8A6';
  $('gateNote').textContent='That is the whole mechanic. Every system we ship behaves exactly like this — it waits.';
  pushLog('approved by operator');
  pushLog('released to scheduler');
}
$('hudApprove').addEventListener('click',approve);
$('q1go').addEventListener('click',approve);
})();
