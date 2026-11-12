var M=globalThis,D=M.ShadowRoot&&(M.ShadyCSS===void 0||M.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,j=Symbol(),se=new WeakMap,S=class{constructor(e,t,s){if(this._$cssResult$=!0,s!==j)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t}get styleSheet(){let e=this.o,t=this.t;if(D&&e===void 0){let s=t!==void 0&&t.length===1;s&&(e=se.get(t)),e===void 0&&((this.o=e=new CSSStyleSheet).replaceSync(this.cssText),s&&se.set(t,e))}return e}toString(){return this.cssText}},ie=n=>new S(typeof n=="string"?n:n+"",void 0,j),H=(n,...e)=>{let t=n.length===1?n[0]:e.reduce((s,i,a)=>s+(r=>{if(r._$cssResult$===!0)return r.cssText;if(typeof r=="number")return r;throw Error("Value passed to 'css' function must be a 'css' function result: "+r+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+n[a+1],n[0]);return new S(t,n,j)},ae=(n,e)=>{if(D)n.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(let t of e){let s=document.createElement("style"),i=M.litNonce;i!==void 0&&s.setAttribute("nonce",i),s.textContent=t.cssText,n.appendChild(s)}},I=D?n=>n:n=>n instanceof CSSStyleSheet?(e=>{let t="";for(let s of e.cssRules)t+=s.cssText;return ie(t)})(n):n;var{is:Ee,defineProperty:ke,getOwnPropertyDescriptor:Ce,getOwnPropertyNames:Te,getOwnPropertySymbols:Ne,getPrototypeOf:Pe}=Object,L=globalThis,ne=L.trustedTypes,Re=ne?ne.emptyScript:"",Oe=L.reactiveElementPolyfillSupport,E=(n,e)=>n,F={toAttribute(n,e){switch(e){case Boolean:n=n?Re:null;break;case Object:case Array:n=n==null?n:JSON.stringify(n)}return n},fromAttribute(n,e){let t=n;switch(e){case Boolean:t=n!==null;break;case Number:t=n===null?null:Number(n);break;case Object:case Array:try{t=JSON.parse(n)}catch{t=null}}return t}},oe=(n,e)=>!Ee(n,e),re={attribute:!0,type:String,converter:F,reflect:!1,useDefault:!1,hasChanged:oe};Symbol.metadata??=Symbol("metadata"),L.litPropertyMetadata??=new WeakMap;var g=class extends HTMLElement{static addInitializer(e){this._$Ei(),(this.l??=[]).push(e)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(e,t=re){if(t.state&&(t.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(e)&&((t=Object.create(t)).wrapped=!0),this.elementProperties.set(e,t),!t.noAccessor){let s=Symbol(),i=this.getPropertyDescriptor(e,s,t);i!==void 0&&ke(this.prototype,e,i)}}static getPropertyDescriptor(e,t,s){let{get:i,set:a}=Ce(this.prototype,e)??{get(){return this[t]},set(r){this[t]=r}};return{get:i,set(r){let c=i?.call(this);a?.call(this,r),this.requestUpdate(e,c,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(e){return this.elementProperties.get(e)??re}static _$Ei(){if(this.hasOwnProperty(E("elementProperties")))return;let e=Pe(this);e.finalize(),e.l!==void 0&&(this.l=[...e.l]),this.elementProperties=new Map(e.elementProperties)}static finalize(){if(this.hasOwnProperty(E("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(E("properties"))){let t=this.properties,s=[...Te(t),...Ne(t)];for(let i of s)this.createProperty(i,t[i])}let e=this[Symbol.metadata];if(e!==null){let t=litPropertyMetadata.get(e);if(t!==void 0)for(let[s,i]of t)this.elementProperties.set(s,i)}this._$Eh=new Map;for(let[t,s]of this.elementProperties){let i=this._$Eu(t,s);i!==void 0&&this._$Eh.set(i,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(e){let t=[];if(Array.isArray(e)){let s=new Set(e.flat(1/0).reverse());for(let i of s)t.unshift(I(i))}else e!==void 0&&t.push(I(e));return t}static _$Eu(e,t){let s=t.attribute;return s===!1?void 0:typeof s=="string"?s:typeof e=="string"?e.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(e=>this.enableUpdating=e),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(e=>e(this))}addController(e){(this._$EO??=new Set).add(e),this.renderRoot!==void 0&&this.isConnected&&e.hostConnected?.()}removeController(e){this._$EO?.delete(e)}_$E_(){let e=new Map,t=this.constructor.elementProperties;for(let s of t.keys())this.hasOwnProperty(s)&&(e.set(s,this[s]),delete this[s]);e.size>0&&(this._$Ep=e)}createRenderRoot(){let e=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return ae(e,this.constructor.elementStyles),e}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(e=>e.hostConnected?.())}enableUpdating(e){}disconnectedCallback(){this._$EO?.forEach(e=>e.hostDisconnected?.())}attributeChangedCallback(e,t,s){this._$AK(e,s)}_$ET(e,t){let s=this.constructor.elementProperties.get(e),i=this.constructor._$Eu(e,s);if(i!==void 0&&s.reflect===!0){let a=(s.converter?.toAttribute!==void 0?s.converter:F).toAttribute(t,s.type);this._$Em=e,a==null?this.removeAttribute(i):this.setAttribute(i,a),this._$Em=null}}_$AK(e,t){let s=this.constructor,i=s._$Eh.get(e);if(i!==void 0&&this._$Em!==i){let a=s.getPropertyOptions(i),r=typeof a.converter=="function"?{fromAttribute:a.converter}:a.converter?.fromAttribute!==void 0?a.converter:F;this._$Em=i;let c=r.fromAttribute(t,a.type);this[i]=c??this._$Ej?.get(i)??c,this._$Em=null}}requestUpdate(e,t,s,i=!1,a){if(e!==void 0){let r=this.constructor;if(i===!1&&(a=this[e]),s??=r.getPropertyOptions(e),!((s.hasChanged??oe)(a,t)||s.useDefault&&s.reflect&&a===this._$Ej?.get(e)&&!this.hasAttribute(r._$Eu(e,s))))return;this.C(e,t,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(e,t,{useDefault:s,reflect:i,wrapped:a},r){s&&!(this._$Ej??=new Map).has(e)&&(this._$Ej.set(e,r??t??this[e]),a!==!0||r!==void 0)||(this._$AL.has(e)||(this.hasUpdated||s||(t=void 0),this._$AL.set(e,t)),i===!0&&this._$Em!==e&&(this._$Eq??=new Set).add(e))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}let e=this.scheduleUpdate();return e!=null&&await e,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,a]of this._$Ep)this[i]=a;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[i,a]of s){let{wrapped:r}=a,c=this[i];r!==!0||this._$AL.has(i)||c===void 0||this.C(i,void 0,a,c)}}let e=!1,t=this._$AL;try{e=this.shouldUpdate(t),e?(this.willUpdate(t),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(t)):this._$EM()}catch(s){throw e=!1,this._$EM(),s}e&&this._$AE(t)}willUpdate(e){}_$AE(e){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(e){return!0}update(e){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(e){}firstUpdated(e){}};g.elementStyles=[],g.shadowRootOptions={mode:"open"},g[E("elementProperties")]=new Map,g[E("finalized")]=new Map,Oe?.({ReactiveElement:g}),(L.reactiveElementVersions??=[]).push("2.1.2");var K=globalThis,le=n=>n,U=K.trustedTypes,de=U?U.createPolicy("lit-html",{createHTML:n=>n}):void 0,ge="$lit$",v=`lit$${Math.random().toFixed(9).slice(2)}$`,_e="?"+v,Me=`<${_e}>`,y=document,C=()=>y.createComment(""),T=n=>n===null||typeof n!="object"&&typeof n!="function",J=Array.isArray,De=n=>J(n)||typeof n?.[Symbol.iterator]=="function",z=`[ 	
\f\r]`,k=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ce=/-->/g,he=/>/g,$=RegExp(`>|${z}(?:([^\\s"'>=/]+)(${z}*=${z}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),pe=/'/g,ue=/"/g,ve=/^(?:script|style|textarea|title)$/i,Y=n=>(e,...t)=>({_$litType$:n,strings:e,values:t}),o=Y(1),Qe=Y(2),et=Y(3),x=Symbol.for("lit-noChange"),d=Symbol.for("lit-nothing"),me=new WeakMap,b=y.createTreeWalker(y,129);function fe(n,e){if(!J(n)||!n.hasOwnProperty("raw"))throw Error("invalid template strings array");return de!==void 0?de.createHTML(e):e}var Le=(n,e)=>{let t=n.length-1,s=[],i,a=e===2?"<svg>":e===3?"<math>":"",r=k;for(let c=0;c<t;c++){let l=n[c],h,u,p=-1,m=0;for(;m<l.length&&(r.lastIndex=m,u=r.exec(l),u!==null);)m=r.lastIndex,r===k?u[1]==="!--"?r=ce:u[1]!==void 0?r=he:u[2]!==void 0?(ve.test(u[2])&&(i=RegExp("</"+u[2],"g")),r=$):u[3]!==void 0&&(r=$):r===$?u[0]===">"?(r=i??k,p=-1):u[1]===void 0?p=-2:(p=r.lastIndex-u[2].length,h=u[1],r=u[3]===void 0?$:u[3]==='"'?ue:pe):r===ue||r===pe?r=$:r===ce||r===he?r=k:(r=$,i=void 0);let _=r===$&&n[c+1].startsWith("/>")?" ":"";a+=r===k?l+Me:p>=0?(s.push(h),l.slice(0,p)+ge+l.slice(p)+v+_):l+v+(p===-2?c:_)}return[fe(n,a+(n[t]||"<?>")+(e===2?"</svg>":e===3?"</math>":"")),s]},N=class n{constructor({strings:e,_$litType$:t},s){let i;this.parts=[];let a=0,r=0,c=e.length-1,l=this.parts,[h,u]=Le(e,t);if(this.el=n.createElement(h,s),b.currentNode=this.el.content,t===2||t===3){let p=this.el.content.firstChild;p.replaceWith(...p.childNodes)}for(;(i=b.nextNode())!==null&&l.length<c;){if(i.nodeType===1){if(i.hasAttributes())for(let p of i.getAttributeNames())if(p.endsWith(ge)){let m=u[r++],_=i.getAttribute(p).split(v),O=/([.?@])?(.*)/.exec(m);l.push({type:1,index:a,name:O[2],strings:_,ctor:O[1]==="."?W:O[1]==="?"?V:O[1]==="@"?q:A}),i.removeAttribute(p)}else p.startsWith(v)&&(l.push({type:6,index:a}),i.removeAttribute(p));if(ve.test(i.tagName)){let p=i.textContent.split(v),m=p.length-1;if(m>0){i.textContent=U?U.emptyScript:"";for(let _=0;_<m;_++)i.append(p[_],C()),b.nextNode(),l.push({type:2,index:++a});i.append(p[m],C())}}}else if(i.nodeType===8)if(i.data===_e)l.push({type:2,index:a});else{let p=-1;for(;(p=i.data.indexOf(v,p+1))!==-1;)l.push({type:7,index:a}),p+=v.length-1}a++}}static createElement(e,t){let s=y.createElement("template");return s.innerHTML=e,s}};function w(n,e,t=n,s){if(e===x)return e;let i=s!==void 0?t._$Co?.[s]:t._$Cl,a=T(e)?void 0:e._$litDirective$;return i?.constructor!==a&&(i?._$AO?.(!1),a===void 0?i=void 0:(i=new a(n),i._$AT(n,t,s)),s!==void 0?(t._$Co??=[])[s]=i:t._$Cl=i),i!==void 0&&(e=w(n,i._$AS(n,e.values),i,s)),e}var B=class{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(e){let{el:{content:t},parts:s}=this._$AD,i=(e?.creationScope??y).importNode(t,!0);b.currentNode=i;let a=b.nextNode(),r=0,c=0,l=s[0];for(;l!==void 0;){if(r===l.index){let h;l.type===2?h=new P(a,a.nextSibling,this,e):l.type===1?h=new l.ctor(a,l.name,l.strings,this,e):l.type===6&&(h=new G(a,this,e)),this._$AV.push(h),l=s[++c]}r!==l?.index&&(a=b.nextNode(),r++)}return b.currentNode=y,i}p(e){let t=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(e,s,t),t+=s.strings.length-2):s._$AI(e[t])),t++}},P=class n{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(e,t,s,i){this.type=2,this._$AH=d,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let e=this._$AA.parentNode,t=this._$AM;return t!==void 0&&e?.nodeType===11&&(e=t.parentNode),e}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(e,t=this){e=w(this,e,t),T(e)?e===d||e==null||e===""?(this._$AH!==d&&this._$AR(),this._$AH=d):e!==this._$AH&&e!==x&&this._(e):e._$litType$!==void 0?this.$(e):e.nodeType!==void 0?this.T(e):De(e)?this.k(e):this._(e)}O(e){return this._$AA.parentNode.insertBefore(e,this._$AB)}T(e){this._$AH!==e&&(this._$AR(),this._$AH=this.O(e))}_(e){this._$AH!==d&&T(this._$AH)?this._$AA.nextSibling.data=e:this.T(y.createTextNode(e)),this._$AH=e}$(e){let{values:t,_$litType$:s}=e,i=typeof s=="number"?this._$AC(e):(s.el===void 0&&(s.el=N.createElement(fe(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(t);else{let a=new B(i,this),r=a.u(this.options);a.p(t),this.T(r),this._$AH=a}}_$AC(e){let t=me.get(e.strings);return t===void 0&&me.set(e.strings,t=new N(e)),t}k(e){J(this._$AH)||(this._$AH=[],this._$AR());let t=this._$AH,s,i=0;for(let a of e)i===t.length?t.push(s=new n(this.O(C()),this.O(C()),this,this.options)):s=t[i],s._$AI(a),i++;i<t.length&&(this._$AR(s&&s._$AB.nextSibling,i),t.length=i)}_$AR(e=this._$AA.nextSibling,t){for(this._$AP?.(!1,!0,t);e!==this._$AB;){let s=le(e).nextSibling;le(e).remove(),e=s}}setConnected(e){this._$AM===void 0&&(this._$Cv=e,this._$AP?.(e))}},A=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(e,t,s,i,a){this.type=1,this._$AH=d,this._$AN=void 0,this.element=e,this.name=t,this._$AM=i,this.options=a,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=d}_$AI(e,t=this,s,i){let a=this.strings,r=!1;if(a===void 0)e=w(this,e,t,0),r=!T(e)||e!==this._$AH&&e!==x,r&&(this._$AH=e);else{let c=e,l,h;for(e=a[0],l=0;l<a.length-1;l++)h=w(this,c[s+l],t,l),h===x&&(h=this._$AH[l]),r||=!T(h)||h!==this._$AH[l],h===d?e=d:e!==d&&(e+=(h??"")+a[l+1]),this._$AH[l]=h}r&&!i&&this.j(e)}j(e){e===d?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,e??"")}},W=class extends A{constructor(){super(...arguments),this.type=3}j(e){this.element[this.name]=e===d?void 0:e}},V=class extends A{constructor(){super(...arguments),this.type=4}j(e){this.element.toggleAttribute(this.name,!!e&&e!==d)}},q=class extends A{constructor(e,t,s,i,a){super(e,t,s,i,a),this.type=5}_$AI(e,t=this){if((e=w(this,e,t,0)??d)===x)return;let s=this._$AH,i=e===d&&s!==d||e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive,a=e!==d&&(s===d||i);i&&this.element.removeEventListener(this.name,this,s),a&&this.element.addEventListener(this.name,this,e),this._$AH=e}handleEvent(e){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,e):this._$AH.handleEvent(e)}},G=class{constructor(e,t,s){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(e){w(this,e)}};var Ue=K.litHtmlPolyfillSupport;Ue?.(N,P),(K.litHtmlVersions??=[]).push("3.3.3");var $e=(n,e,t)=>{let s=t?.renderBefore??e,i=s._$litPart$;if(i===void 0){let a=t?.renderBefore??null;s._$litPart$=i=new P(e.insertBefore(C(),a),a,void 0,t??{})}return i._$AI(n),i};var X=globalThis,f=class extends g{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let e=super.createRenderRoot();return this.renderOptions.renderBefore??=e.firstChild,e}update(e){let t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=$e(t,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return x}};f._$litElement$=!0,f.finalized=!0,X.litElementHydrateSupport?.({LitElement:f});var je=X.litElementPolyfillSupport;je?.({LitElement:f});(X.litElementVersions??=[]).push("4.2.2");var R=[["labels","Labels"],["areas","Areas"],["floors","Floors"],["domains","Domains"],["devices","Devices"],["entities","Entities"],["groups","Groups"],["capabilities","Capabilities"],["integrations","Integrations"],["manufacturers","Manufacturers"],["models","Models"],["entity_categories","Entity categories"],["name_patterns","Name or entity id patterns"],["label_patterns","Label name patterns"],["states","Current state"],["conditions","Conditions on state or attributes"]],Z=["states","conditions"],He=["on","off","unavailable","unknown","open","closed","home","not_home","locked","unlocked","playing","idle","paused"],Ie=[["<","is below"],["<=","is at most"],[">","is above"],[">=","is at least"],["=","is"],["!=","is not"],["between","is between"]];function be(n){let[e="state",t="<",...s]=String(n).trim().split(/\s+/),i=e==="state"?"state":"attr",a=e.startsWith("attr:")?e.slice(5):"";return t==="between"?{source:i,attr:a,op:t,a:s[0]||"",b:s[1]||""}:{source:i,attr:a,op:t,a:s.join(" "),b:""}}var ye=n=>(n.source==="state"||n.attr.trim())&&String(n.a).trim()&&(n.op!=="between"||String(n.b).trim()),Fe=n=>`${n.source==="state"?"state":`attr:${n.attr.trim()}`} ${n.op} ${n.op==="between"?`${String(n.a).trim()} ${String(n.b).trim()}`:String(n.a).trim()}`,xe=["integrations","manufacturers","models","entity_categories","name_patterns","label_patterns"],Q={integrations:"Where the entity comes from, for example hue or zha.",manufacturers:"Of the entity's device. Wildcards work: IKEA*.",models:"Of the entity's device. Wildcards work.",entity_categories:"Primary entities are the ones with no category. Config and diagnostic entities are the extras integrations add.",name_patterns:"Matches the entity id or its name, ignoring case. Use * for any text and ? for one character, for example switch.*_plug or *outlet*.",label_patterns:"Matches label names, ignoring case, for example Expose: * for every label that starts that way.",states:"The entity's state right now, for example on or unavailable. Any of the values will do.",conditions:"Matches if any of these hold. The rule re-checks whenever an entity's state changes across a condition."},ze=[{value:"primary",label:"Primary (no category)"},{value:"config",label:"Config"},{value:"diagnostic",label:"Diagnostic"}],we=[{value:"onoff",label:"Light: on/off only"},{value:"brightness",label:"Light: brightness"},{value:"color_temp",label:"Light: white temperature"},{value:"color",label:"Light: color"},{value:"white",label:"Light: white channel"},{value:"position",label:"Cover: set position"},{value:"tilt",label:"Cover: set tilt"},{value:"speed",label:"Fan: speed"},{value:"oscillate",label:"Fan: oscillate"},{value:"direction",label:"Fan: direction"},{value:"preset",label:"Fan: preset modes"},{value:"heat",label:"Climate: heat"},{value:"cool",label:"Climate: cool"},{value:"heat_cool",label:"Climate: heat/cool"},{value:"auto",label:"Climate: auto"},{value:"dry",label:"Climate: dry"},{value:"fan_only",label:"Climate: fan only"},{value:"target_temp",label:"Climate: target temperature"}],Be=["device_classes"],We=26,Ve=[["rules","Rules"],["status","Status"],["explain","Explain"],["settings","Settings"]],qe=(n,e=0)=>({hours:n,minutes:e,seconds:0}),Ge=[{id:"auto_off",title:"Auto-off timer",text:"Turn outlets off after they have been on for a while. Survives restarts and respects manual switching.",make:()=>({name:"Auto-off outlets",include:{domains:["switch"]},actions:[{type:"schedule",config:{trigger:"state_for",state:"on",do:"turn_off",duration:qe(3)}}]})},{id:"sunset_on",title:"Lights on at sunset",text:"Turn lights on at sunset, with an optional offset.",make:()=>({name:"Lights on at sunset",include:{domains:["light"]},actions:[{type:"schedule",config:{trigger:"sun",event:"sunset",offset_minutes:0,do:"turn_on",catch_up_minutes:30}}]})},{id:"night_off",title:"Lights off at night",text:"Turn lights off at a set time of day.",make:()=>({name:"Lights off at night",include:{domains:["light"]},actions:[{type:"schedule",config:{trigger:"time",at:"23:00:00",do:"turn_off",catch_up_minutes:0}}]})},{id:"expose",title:"Expose to a voice assistant",text:"Let Assist, Alexa or Google see the entities with a label.",make:()=>({name:"Voice assistant exposure",include:{},actions:[{type:"expose",config:{assistants:["conversation"]}}]})},{id:"group",title:"Keep a group in sync",text:"Fill a group with the entities a rule selects, for example every light with white temperature.",make:()=>({name:"Dynamic group",include:{},actions:[{type:"group",config:{create_name:"",group_type:"light"}}]})},{id:"metrics",title:"Ship numeric history",text:"Send the numeric history of entities (by label, integration, name\u2026) to your metrics endpoint. Needs the permission in Settings.",make:()=>({name:"Ship metrics",include:{},actions:[{type:"metrics",config:{min_interval_seconds:60,include_booleans:!1,tag_area:!0,tag_device_class:!0,tag_unit:!0,max_entities:200}}]})},{id:"label",title:"Apply a label automatically",text:"Tag entities from their metadata, for example every battery below 20% gets \u201CNeeds battery\u201D.",make:()=>({name:"Auto label",include:{conditions:["attr:battery_level < 20"]},actions:[{type:"label",config:{name:"Needs battery"}}]})},{id:"aliases",title:"Give a voice alias",text:"Selected entities also answer to an extra name in Assist, Alexa or Google.",make:()=>({name:"Voice alias",include:{},actions:[{type:"aliases",config:{aliases:[]}}]})},{id:"flag",title:"Flag in Repairs (hygiene check)",text:"List entities that match in Home Assistant's Repairs, for example lights with no label.",make:()=>({name:"Hygiene check",include:{domains:["light"]},exclude:{label_patterns:["*"]},actions:[{type:"flag",config:{title:"Lights without a label"}}]})},{id:"dashboard",title:"Show on a dashboard",text:"Build a dashboard section from a rule, for example the lights a guest or wall tablet may see. Dashboards stay in sync with the rule.",make:()=>({name:"Guest lights",include:{domains:["light"]},actions:[{type:"dashboard",config:{dashboard:"guest",title:"Lights",group_by:"area",audience:["non-admins"]}}]})},{id:"run",title:"Run actions when something enters",text:"Notify or call a service when an entity starts matching, for example when it gets a label. First sight fires nothing.",make:()=>({name:"On enter",include:{},actions:[{type:"run",config:{on_enter:[],on_leave:[],max_per_run:20}}]})},{id:"blank",title:"Start from scratch",text:"An empty rule.",make:()=>({})}],ee=()=>Object.fromEntries([...R.map(([n])=>n),...Be].map(n=>[n,[]])),Ae=()=>({name:"",enabled:!0,include:ee(),exclude:ee(),actions:[{type:"expose",config:{assistants:["conversation"]}}]}),Se=n=>!Object.values(n||{}).some(e=>e&&e.length);async function Ke(){try{if(customElements.get("ha-selector")&&customElements.get("ha-form"))return;await(await(await window.loadCardHelpers?.())?.createCardElement({type:"entities",entities:[]}))?.constructor?.getConfigElement?.()}catch{}}var te=class extends f{static properties={hass:{attribute:!1},narrow:{type:Boolean},panel:{attribute:!1},_tab:{state:!0},_data:{state:!0},_error:{state:!0},_busy:{state:!0},_editing:{state:!0},_preview:{state:!0},_applyResult:{state:!0},_explain:{state:!0},_explainEntity:{state:!0},_settingsDraft:{state:!0},_showAll:{state:!0},_choosing:{state:!0},_toastMsg:{state:!0}};constructor(){super(),this._tab="rules",this._data=null,this._error="",this._busy=!1,this._editing=null,this._preview=null,this._applyResult=null,this._explain=null,this._explainEntity="",this._settingsDraft=null,this._showAll=!1,this._choosing=!1,this._toastMsg="",this._previewTimer=null}async connectedCallback(){super.connectedCallback(),await Ke(),await Promise.all([this._load(),this._loadNames()])}_ws(e){return this.hass.callWS(e)}async _load(){try{this._data=await this._ws({type:"propsense/overview"}),this._settingsDraft={...this._data.settings},this._error=""}catch(e){this._error=e.message||String(e)}}_toast(e){this._toastMsg=e,clearTimeout(this._toastTimer),this._toastTimer=setTimeout(()=>this._toastMsg="",3500)}_rel(e){let t=new Date(e).getTime()-Date.now(),s=Math.abs(t),i=Math.round(s/6e4),a=i>=60?`${Math.floor(i/60)} h ${i%60} min`:`${i} min`;return t>=0?`in ${a}`:`${a} ago (waiting)`}async _run(e){this._busy=!0;try{await e(),this._error=""}catch(t){this._error=t.message||String(t)}finally{this._busy=!1}}async _loadNames(){this._names={labels:{},areas:{},floors:{}};let e=[["labels","config/label_registry/list","label_id"],["areas","config/area_registry/list","area_id"],["floors","config/floor_registry/list","floor_id"]];await Promise.all(e.map(async([t,s,i])=>{try{for(let a of await this._ws({type:s}))this._names[t][a[i]]=a.name}catch{}})),this.requestUpdate()}_labelName(e){return this._names?.labels?.[e]??this.hass.labels?.[e]?.name??e}_areaName(e){return this._names?.areas?.[e]??this.hass.areas?.[e]?.name??e}_floorName(e){return this._names?.floors?.[e]??this.hass.floors?.[e]?.name??e}_deviceName(e){let t=this.hass.devices?.[e];return t?.name_by_user||t?.name||e}_entityName(e){return this.hass.states?.[e]?.attributes?.friendly_name||e}_valueName(e,t){switch(e){case"labels":return this._labelName(t);case"areas":return this._areaName(t);case"floors":return this._floorName(t);case"devices":return this._deviceName(t);case"capabilities":return we.find(s=>s.value===t)?.label??t;case"entities":case"groups":return this._entityName(t);default:return t}}_targetName(e,t){let s=this._data?.assistants?.find(i=>i.value===t);return e==="expose"&&s?s.label:t}_typeName(e){return this._data?.actions?.find(t=>t.type===e)?.name||e}_summarise(e){let t=R.filter(([s])=>e?.[s]?.length).map(([s,i])=>`${i}: ${e[s].map(a=>this._valueName(s,a)).join(", ")}`);return t.length?t.join(" \xB7 "):""}_countFor(e){let t=this._data?.last?.rules?.[e.name];return t===void 0?"\u2013":t}async _toggle(e){await this._run(async()=>{await this._ws({type:"propsense/rule/save",rule:{...e,enabled:!e.enabled}}),await this._applyAfterChange(),this._toast(e.enabled?`Disabled \u201C${e.name}\u201D`:`Enabled \u201C${e.name}\u201D`)})}async _delete(e){confirm(`Delete the rule "${e.name}"?`)&&await this._run(async()=>{await this._ws({type:"propsense/rule/delete",rule_id:e.id}),await this._applyAfterChange()})}async _applyAfterChange(){await this._ws({type:"propsense/apply",dry_run:!1}),await this._load()}_edit(e){this._choosing=!1,this._condDrafts=null,this._editing={...Ae(),...JSON.parse(JSON.stringify(e||Ae()))};for(let t of["include","exclude"])this._editing[t]={...ee(),...this._editing[t]};this._preview=null,this._showAll=!1,this._schedulePreview()}_setEditing(e){this._editing={...this._editing,...e},this._schedulePreview()}_setSelector(e,t,s){this._setEditing({[e]:{...this._editing[e],[t]:s||[]}})}_schedulePreview(){clearTimeout(this._previewTimer),this._previewTimer=setTimeout(()=>this._runPreview(),400)}async _runPreview(){if(!this._editing)return;let e=this._cleanRule();e.name||(e.name="(draft)");try{this._preview=await this._ws({type:"propsense/preview",rule:e})}catch(t){this._preview={error:t.message||String(t)}}}_cleanRule(){let{id:e,name:t,enabled:s,include:i,exclude:a,actions:r}=this._editing;return{...e?{id:e}:{},name:(t||"").trim(),enabled:s,include:i,exclude:a,actions:r}}async _save(){let e=this._cleanRule();if(!e.name){this._error="Give the rule a name.";return}await this._run(async()=>{await this._ws({type:"propsense/rule/save",rule:e}),this._editing=null,await this._applyAfterChange(),this._toast(`Saved \u201C${e.name}\u201D`)})}_addAction(){let e=this._data.actions.find(s=>s.available)?.type||this._data.actions[0].type,t=this._defaultConfig(e);this._setEditing({actions:[...this._editing.actions,{type:e,config:t}]})}_defaultConfig(e){let t=this._data.actions.find(s=>s.type===e)?.schema||[];return Object.fromEntries(t.filter(s=>s.default!==void 0).map(s=>[s.name,s.default]))}_setAction(e,t){let s=this._editing.actions.map((i,a)=>e===a?{...i,...t}:i);this._setEditing({actions:s})}_removeAction(e){this._setEditing({actions:this._editing.actions.filter((t,s)=>s!==e)})}render(){return!this._data&&!this._error?o`<div class="loading">Loading…</div>`:o`
      <div class="toolbar">
        ${this.narrow?o`<ha-menu-button .hass=${this.hass} .narrow=${this.narrow}></ha-menu-button>`:d}
        <div class="title">PropSense</div>
      </div>
      <div class="tabs">
        ${Ve.map(([e,t])=>o`<button
            class="tab ${this._tab===e?"active":""}"
            @click=${()=>this._tab=e}
          >${t}</button>`)}
      </div>
      ${this._toastMsg?o`<div class="toast">${this._toastMsg}</div>`:d}
      <div class="content">
        ${this._error?o`<div class="error">${this._error}</div>`:d}
        ${this._data?this._renderTab():d}
      </div>
    `}_renderTab(){if(this._editing&&this._tab==="rules")return this._renderEditor();switch(this._tab){case"status":return this._renderStatus();case"explain":return this._renderExplain();case"settings":return this._renderSettings();default:return this._renderRules()}}_renderRules(){let{rules:e,settings:t}=this._data;return o`
      ${!e.length&&!t.dry_run?o`<div class="notice warn">
            <b>Start with a dry run.</b> Rules are the single source of truth: with no rules,
            everything an assistant PropSense manages can see is un-exposed on the next apply.
            <button @click=${()=>this._setDryRun(!0)}>Turn on dry run</button>
          </div>`:d}
      ${t.dry_run?o`<div class="notice">
            Dry run is on: rules are evaluated but nothing is applied.
            <button @click=${()=>this._setDryRun(!1)}>Turn off</button>
          </div>`:d}
      <div class="row">
        <h2>Rules</h2>
        <button class="primary" @click=${()=>this._choosing=!this._choosing}>Add rule</button>
      </div>
      ${this._choosing?this._renderChooser():d}
      ${e.length?e.map(s=>this._renderRuleCard(s)):o`<p class="muted">No rules yet. A rule selects entities, for example everything labelled
            “Expose: Voice”, and applies actions such as exposing them to Assist.</p>`}
    `}_renderChooser(){return o`<div class="templates">
      ${Ge.map(e=>o`<button class="template" @click=${()=>this._edit(e.make())}>
          <div class="rule-name">${e.title}</div>
          <div class="muted">${e.text}</div>
        </button>`)}
    </div>`}async _setDryRun(e){await this._run(async()=>{await this._ws({type:"propsense/settings/update",settings:{dry_run:e}}),await new Promise(t=>setTimeout(t,1500)),await this._load()})}_renderRuleCard(e){let t=this._summarise(e.include),s=this._summarise(e.exclude),i=this._data.last?.dormant?.[e.name];return o`<ha-card class="rule ${e.enabled?"":"off"}">
      <div class="rule-head">
        <div>
          <div class="rule-name">${e.name}</div>
          <div class="muted">${this._countFor(e)} ${this._countFor(e)===1?"entity":"entities"}</div>
          <ul class="summary">
            ${(this._data.summaries?.[e.id]||[]).map(a=>o`<li>${a}</li>`)}
          </ul>
        </div>
        <div class="rule-actions">
          <label class="switch" title="Enable or disable">
            <input type="checkbox" .checked=${e.enabled} @change=${()=>this._toggle(e)} />
            ${e.enabled?"On":"Off"}
          </label>
          <button @click=${()=>this._edit(e)}>Edit</button>
          <button class="danger" @click=${()=>this._delete(e)}>Delete</button>
        </div>
      </div>
      <div class="sel">${t||o`<span class="warn-text">Selects nothing (no include fields).</span>`}</div>
      ${s?o`<div class="sel muted">Except: ${s}</div>`:d}
      ${i?o`<div class="warn-text">Dormant action: ${i.join(", ")}. Needs the provider, and the matching permission in Settings.</div>`:d}
    </ha-card>`}_selectorFor(e){switch(e){case"labels":return{label:{multiple:!0}};case"areas":return{area:{multiple:!0}};case"floors":return{floor:{multiple:!0}};case"devices":return{device:{multiple:!0}};case"entities":case"groups":return{entity:{multiple:!0}};case"capabilities":return{select:{multiple:!0,options:we}};case"entity_categories":return{select:{multiple:!0,options:ze}};case"integrations":case"manufacturers":case"models":return{select:{multiple:!0,custom_value:!0,options:this._data?.choices?.[e]||[]}};case"name_patterns":case"label_patterns":return{select:{multiple:!0,custom_value:!0,options:[]}};case"states":return{select:{multiple:!0,custom_value:!0,options:He}};default:return{select:{multiple:!0,custom_value:!0,options:[...new Set(Object.keys(this.hass.states).map(s=>s.split(".")[0]))].sort()}}}}_renderSelectorFields(e){let t=this._editing[e],s=([h,u])=>o`<div class="field">
      <div class="label">${u}</div>
      ${Q[h]?o`<div class="muted help">${Q[h]}</div>`:d}
      <ha-selector
        .hass=${this.hass}
        .selector=${this._selectorFor(h)}
        .value=${t[h]||[]}
        @value-changed=${p=>this._setSelector(e,h,p.detail.value)}
      ></ha-selector>
    </div>`,i=R.filter(([h])=>!xe.includes(h)&&!Z.includes(h)),a=R.filter(([h])=>xe.includes(h)),r=a.some(([h])=>t[h]?.length),c=Z.some(h=>t[h]?.length),l=([h,u])=>h==="conditions"?this._renderConditions(e,u):s([h,u]);return o`${i.map(s)}
      <details class="more" ?open=${r}>
        <summary>More filters: integration, manufacturer, name patterns…</summary>
        ${a.map(s)}
      </details>
      <details class="more" ?open=${c}>
        <summary>Current state and attributes: battery below 20%, currently on…</summary>
        ${R.filter(([h])=>Z.includes(h)).map(l)}
      </details>`}_condRows(e){return this._condDrafts||(this._condDrafts={include:(this._editing.include.conditions||[]).map(be),exclude:(this._editing.exclude.conditions||[]).map(be)}),this._condDrafts[e]}_setCondRows(e,t){this._condDrafts[e]=t,this._setSelector(e,"conditions",t.filter(ye).map(Fe))}_renderConditions(e,t){let s=this._condRows(e),i=(a,r)=>this._setCondRows(e,s.map((c,l)=>a===l?{...c,...r}:c));return o`<div class="field">
      <div class="label">${t}</div>
      <div class="muted help">${Q.conditions}</div>
      ${s.map((a,r)=>o`<div class="line cond">
        <select @change=${c=>i(r,{source:c.target.value})}>
          <option value="state" ?selected=${a.source==="state"}>State</option>
          <option value="attr" ?selected=${a.source==="attr"}>Attribute</option>
        </select>
        ${a.source==="attr"?o`<input type="text" class="attr" placeholder="battery_level" .value=${a.attr}
              @input=${c=>i(r,{attr:c.target.value})} />`:d}
        <select @change=${c=>i(r,{op:c.target.value})}>
          ${Ie.map(([c,l])=>o`<option value=${c} ?selected=${a.op===c}>${l}</option>`)}
        </select>
        <input type="text" class="val" .value=${a.a} placeholder=${a.op==="between"?"from":"value"}
          @input=${c=>i(r,{a:c.target.value})} />
        ${a.op==="between"?o`<span>and</span><input type="text" class="val" .value=${a.b} placeholder="to"
              @input=${c=>i(r,{b:c.target.value})} />`:d}
        <button class="danger" type="button" @click=${()=>this._setCondRows(e,s.filter((c,l)=>l!==r))}>Remove</button>
        ${ye(a)?d:o`<span class="warn-text">Incomplete: not used yet.</span>`}
      </div>`)}
      <button type="button" @click=${()=>this._setCondRows(e,[...s,{source:"state",attr:"",op:"<",a:"",b:""}])}>Add condition</button>
    </div>`}_renderEditor(){let e=this._editing;return o`
      <div class="row">
        <h2>${e.id?"Edit rule":"New rule"}</h2>
        <div>
          <button @click=${()=>this._editing=null}>Cancel</button>
          <button class="primary" ?disabled=${this._busy} @click=${this._save}>Save</button>
        </div>
      </div>
      <div class="editor">
        <div class="col">
          <ha-card class="pad">
            <div class="field">
              <div class="label">Name</div>
              <input
                type="text"
                .value=${e.name}
                placeholder="For example: Voice assistant"
                @input=${t=>this._setEditing({name:t.target.value})}
              />
            </div>
            <label class="check">
              <input type="checkbox" .checked=${e.enabled}
                @change=${t=>this._setEditing({enabled:t.target.checked})} />
              Enabled
            </label>
          </ha-card>

          <ha-card class="pad">
            <h3>1 · What does it apply to?</h3>
            <p class="muted">Every field you fill in must match (and); within a field any value will do (or). The live preview shows what is selected.</p>
            ${this._renderSelectorFields("include")}
          </ha-card>

          <ha-card class="pad">
            <details ?open=${!Se(e.exclude)}>
              <summary>Exclude (optional)</summary>
              <p class="muted">Entities matching all the fields you fill in here are removed from this rule.</p>
              ${this._renderSelectorFields("exclude")}
            </details>
          </ha-card>

          <ha-card class="pad">
            <div class="row"><h3>2 · What should happen?</h3>
              <button @click=${this._addAction}>Add action</button></div>
            ${e.actions.length?e.actions.map((t,s)=>this._renderAction(t,s)):o`<p class="warn-text">No actions: this rule does nothing.</p>`}
          </ha-card>
        </div>
        <div class="col">${this._renderPreview()}</div>
      </div>
    `}_renderAction(e,t){let s=this._data.actions,i=s.find(r=>r.type===e.type),a=r=>this._labels[r.name]??r.name.replaceAll("_"," ");return o`<div class="action">
      <div class="row">
        <select @change=${r=>this._setAction(t,{type:r.target.value,config:this._defaultConfig(r.target.value)})}>
          ${s.map(r=>o`<option value=${r.type} ?selected=${r.type===e.type} ?disabled=${!r.available&&r.type!==e.type}>
              ${r.name}${r.available?"":r.requires==="external_data"?" (allow sending data in Settings)":" (enable third-party actions)"}
            </option>`)}
          ${i?d:o`<option selected>${e.type} (not installed)</option>`}
        </select>
        <button class="danger" @click=${()=>this._removeAction(t)}>Remove</button>
      </div>
      ${this._actionHelp[e.type]?o`<div class="muted help">${this._actionHelp[e.type]}</div>`:d}
      ${e.type==="schedule"?this._renderSchedule(e,t):d}
      ${i&&e.type!=="schedule"?o`${i.available?d:o`<div class="warn-text">${i.requires==="external_data"?"Dormant: allow sending data off this instance in Settings first. Nothing is sent until you do.":"Dormant until third-party actions are allowed in Settings."}</div>`}
          <ha-form
            .hass=${this.hass}
            .schema=${i.schema}
            .data=${e.config}
            .computeLabel=${a}
            @value-changed=${r=>this._setAction(t,{config:r.detail.value})}
          ></ha-form>`:e.type==="schedule"||i?d:o`<div class="warn-text">This action type is not installed, so the rule is dormant.</div>`}
    </div>`}_renderSchedule(e,t){let s={trigger:"state_for",do:"turn_off",state:"on",event:"sunset",offset_minutes:0,catch_up_minutes:0,days:[],...e.config},i=l=>this._setAction(t,{config:{...s,...l}}),a={hours:0,minutes:0,seconds:0,...s.duration||{}},r=l=>Math.max(0,parseInt(l||"0",10)||0),c=["mon","tue","wed","thu","fri","sat","sun"];return o`<div class="sentence">
      <div class="line">
        <select .value=${s.do} @change=${l=>i({do:l.target.value})}>
          <option value="turn_off" ?selected=${s.do==="turn_off"}>Turn off</option>
          <option value="turn_on" ?selected=${s.do==="turn_on"}>Turn on</option>
        </select>
        <span>the selected entities</span>
        <select .value=${s.trigger} @change=${l=>i({trigger:l.target.value})}>
          <option value="state_for" ?selected=${s.trigger==="state_for"}>after they have been</option>
          <option value="time" ?selected=${s.trigger==="time"}>at a time of day</option>
          <option value="sun" ?selected=${s.trigger==="sun"}>at sunrise or sunset</option>
        </select>
      </div>
      ${s.trigger==="state_for"?o`<div class="line">
            <select .value=${s.state} @change=${l=>i({state:l.target.value})}>
              <option value="on" ?selected=${s.state==="on"}>on</option>
              <option value="off" ?selected=${s.state==="off"}>off</option>
            </select>
            <span>for</span>
            <input class="small" type="number" min="0" .value=${String(a.hours)}
              @input=${l=>i({duration:{...a,hours:r(l.target.value)}})} />
            <span>hours</span>
            <input class="small" type="number" min="0" max="59" .value=${String(a.minutes)}
              @input=${l=>i({duration:{...a,minutes:r(l.target.value)}})} />
            <span>minutes</span>
          </div>
          <p class="muted">Watches the entity's state, so it makes no difference whether it was switched in Home
            Assistant or by hand. If it goes ${s.state==="on"?"off":"on"} first, the timer is cancelled.
            Deadlines are stored, so restarts don't reset them. Entities already ${s.state} when PropSense first
            sees them start their timer then.</p>`:d}
      ${s.trigger==="time"?o`<div class="line"><span>at</span>
            <input type="time" step="60" .value=${(s.at||"").slice(0,5)}
              @input=${l=>i({at:l.target.value?`${l.target.value}:00`:""})} /></div>`:d}
      ${s.trigger==="sun"?o`<div class="line"><span>at</span>
            <select .value=${s.event} @change=${l=>i({event:l.target.value})}>
              <option value="sunrise" ?selected=${s.event==="sunrise"}>sunrise</option>
              <option value="sunset" ?selected=${s.event==="sunset"}>sunset</option>
            </select>
            <input class="small" type="number" .value=${String(s.offset_minutes)}
              @input=${l=>i({offset_minutes:parseInt(l.target.value||"0",10)||0})} />
            <span>minutes (negative is before)</span></div>`:d}
      ${s.trigger!=="state_for"?o`<div class="line"><span>on</span>
            ${c.map(l=>o`<button class="chip ${s.days.includes(l)?"on":""}" type="button"
              @click=${()=>i({days:s.days.includes(l)?s.days.filter(h=>h!==l):[...s.days,l]})}>
              ${l}</button>`)}
            <span class="muted">${s.days.length?"":"(every day)"}</span></div>
          <div class="line"><span>If Home Assistant was down at that time, still run it up to</span>
            <input class="small" type="number" min="0" .value=${String(s.catch_up_minutes)}
              @input=${l=>i({catch_up_minutes:r(l.target.value)})} />
            <span>minutes late (0 = skip)</span></div>
          <p class="muted">Entities already ${s.do==="turn_on"?"on":"off"} are left alone, and a light someone turned
            off by hand stays off until the next time.</p>`:d}
    </div>`}_labels={assistants:"Expose to",group:"Existing group (to edit)",create_name:"Or create a group named",group_type:"Type of group to create",min_interval_seconds:"Seconds between points per entity (at least)",include_booleans:"Also send on/off as 1/0",tag_area:"Tag points with the area",tag_device_class:"Tag points with the device class",tag_unit:"Tag points with the unit",max_entities:"Most entities this rule may ship",name:"Label name",aliases:"Aliases (type and press enter)",title:"Title shown in Repairs",message:"Extra text (optional)",on_enter:"When an entity enters the selection, run",on_leave:"When an entity leaves the selection, run",max_per_run:"Most entities handled per evaluation",dashboard:"Dashboard name (used by the strategy)",group_by:"Group entities by",audience:"Who sees this section (everyone, admins, non-admins, or user ids)"};_actionHelp={label:"Adds this label to every selected entity and removes it from entities that stop matching, even ones labelled by hand. The label is created if missing. Other rules can select on it.",aliases:"Adds these aliases to every selected entity and removes them from entities that stop matching. Other aliases are left alone.",flag:"Lists the selected entities in Repairs under your title; the issue disappears when nothing matches. Changes no entity.",dashboard:"Lists the selected entities in a named section of a PropSense dashboard. Create the dashboard once with the strategy shown in the README (type custom:propsense, dashboard: <name>). Audience limits who is shown the section; it is not a security boundary.",run:"Runs your actions for each entity that starts (or stops) matching. Available in templates: entity_id, event (enter or leave) and name. Adding the rule fires nothing for entities that already match."};_renderPreview(){let e=this._preview,t=this._editing;return o`<ha-card class="pad sticky">
      <h3>Live preview</h3>
      ${Se(t.include)?o`<p class="warn-text">Selects nothing: fill in at least one include field.</p>`:d}
      ${e?e.error?o`<p class="warn-text">${e.error}</p>`:this._renderPreviewBody(e):o`<p class="muted">Working…</p>`}
    </ha-card>`}_renderPreviewBody(e){let t=e.draft,s=t?.entities||[],i=this._showAll?s:s.slice(0,25),a=this._editing.actions.some(r=>r.type==="expose");return o`
      <div class="big">${t?.count??0} <span class="muted">entities selected</span></div>
      ${a?o`<div class="muted">About ${(t?.count??0)*We} prompt tokens if exposed to an LLM agent.</div>`:d}
      ${Object.entries(e.assistants||{}).map(([r,c])=>c.refused?o`<div class="warn-text">${this._targetName("expose",r)}: over the size limit, nothing would change.</div>`:d)}
      ${t?.skipped&&Object.keys(t.skipped).length?o`<div class="warn-text">Skipped: ${Object.entries(t.skipped).map(([r,c])=>`${r} (${c})`).join("; ")}</div>`:d}
      <ul class="entities">
        ${i.map(r=>o`<li><span>${r.name}</span> <span class="muted">${r.entity_id}</span></li>`)}
      </ul>
      ${s.length>i.length?o`<button @click=${()=>this._showAll=!0}>Show all ${s.length}</button>`:d}
    `}_renderStatus(){let e=this._data.last,t=this._applyResult||e;return o`
      <div class="row">
        <h2>Status</h2>
        <div>
          <button ?disabled=${this._busy} @click=${()=>this._apply(!0)}>Dry run</button>
          <button class="primary" ?disabled=${this._busy} @click=${()=>this._apply(!1)}>Apply now</button>
        </div>
      </div>
      ${this._data.settings.dry_run?o`<div class="notice">Dry run is on: “Apply now” changes nothing, and timers and schedules don't fire.</div>`:d}
      ${this._renderRuntime()}
      ${t?o`
            <p class="muted">${t.dry_run?"Dry run":"Last applied"} ${new Date(t.at).toLocaleString()}</p>
            ${this._renderTargets("expose",t.assistants)}
            ${Object.entries(t.actions||{}).map(([s,i])=>this._renderTargets(s,i))}
            ${Object.keys(t.dormant||{}).length?o`<div class="notice warn">Dormant rules: ${Object.entries(t.dormant).map(([s,i])=>`${s} (${i.join(", ")})`).join("; ")}</div>`:d}
            ${Object.keys(t.blocked||{}).length?o`<div class="notice">Skipped (matched a rule but never applied): ${Object.entries(t.blocked).map(([s,i])=>`${s} (${i})`).join("; ")}</div>`:d}
          `:o`<p class="muted">Nothing has been applied yet.</p>`}
    `}_renderMetrics(){let e=this._data.runtime?.metrics;return!e||!e.targets?.length?d:o`<ha-card class="pad">
      <h3>Metrics shipping</h3>
      ${e.url?o`<div class="muted">Sending to <code>${e.url}</code> and nowhere else.</div>`:d}
      ${e.url?d:o`<div class="warn-text">No Metrics URL is set. Set one in Settings; nothing is sent until then.</div>`}
      ${e.targets.map(t=>o`<div>${t.label} · ${t.entities} entities</div>`)}
      <div>Sent ${e.sent} points · waiting to send ${e.buffered}${e.dropped?o` · <span class="warn-text">dropped ${e.dropped}</span>`:d}</div>
      ${e.last_error?o`<div class="warn-text">Last send failed: ${e.last_error}. Points wait in memory and are retried every 30 seconds.</div>`:e.last_success?o`<div class="muted">Last success ${new Date(e.last_success).toLocaleString()}</div>`:d}
    </ha-card>`}_renderRuntime(){let e=this._data.runtime?.schedule?.schedules||[];return e.length?o`${this._renderMetrics()}<ha-card class="pad">
      <h3>Timers and schedules</h3>
      ${e.map(t=>o`<div class="runtime">
        <div><b>${t.label}</b> <span class="muted">· ${t.entities.length} entities</span></div>
        ${t.timers?.length?o`<ul class="summary">${t.timers.map(s=>o`<li>${this._entityName(s.entity_id)}: ${this._rel(s.due)}</li>`)}</ul>`:t.trigger==="state_for"?o`<div class="muted">No running timers: none of them is in that state.</div>`:d}
        ${t.next?o`<div class="muted">Next run ${new Date(t.next).toLocaleString()} (${this._rel(t.next)})</div>`:d}
      </div>`)}
    </ha-card>`:this._renderMetrics()}_renderTargets(e,t){return Object.entries(t||{}).map(([s,i])=>o`<ha-card class="pad">
        <div class="row">
          <div><b>${this._typeName(e)}</b> → ${i.label||this._targetName(e,s)}</div>
          <div>${i.count} entities${e==="expose"?o` · ~${i.estimated_tokens} tokens`:d}</div>
        </div>
        ${i.refused?o`<div class="warn-text">Refused: over the size limit. Nothing was changed.</div>`:d}
        ${i.error?o`<div class="warn-text">Error: ${i.error}</div>`:d}
        ${i.added?.length?o`<div>Adds ${i.added.length}: <span class="muted">${i.added.join(", ")}</span></div>`:d}
        ${i.removed?.length?o`<div>Removes ${i.removed.length}: <span class="muted">${i.removed.join(", ")}</span></div>`:d}
      </ha-card>`)}async _apply(e){await this._run(async()=>{let t=await this._ws({type:"propsense/apply",dry_run:e});this._applyResult=e?t:null,await this._load()})}_renderExplain(){let e=this._explain;return o`
      <h2>Explain an entity</h2>
      <p class="muted">Pick an entity to see which rules select it, and why not.</p>
      <ha-selector
        .hass=${this.hass}
        .selector=${{entity:{}}}
        .value=${this._explainEntity}
        @value-changed=${t=>this._doExplain(t.detail.value)}
      ></ha-selector>
      ${e&&!e.found?o`<p class="warn-text">PropSense doesn't know this entity (it may be disabled).</p>`:d}
      ${e?.found?o`
        <ha-card class="pad">
          <div><b>Labels</b>: ${e.labels.map(t=>this._labelName(t)).join(", ")||"none"}</div>
          <div><b>Area</b>: ${e.area_id?this._areaName(e.area_id):"none"}
            · <b>Floor</b>: ${e.floor_id?this._floorName(e.floor_id):"none"}</div>
          <div><b>Groups</b>: ${e.groups.map(t=>this._entityName(t)).join(", ")||"none"}</div>
          <div><b>Capabilities</b>: ${e.capabilities.map(t=>this._valueName("capabilities",t)).join(", ")||"none"}</div>
          <div><b>Integration</b>: ${e.integration||"none"}
            · <b>Manufacturer</b>: ${e.manufacturer||"none"} · <b>Model</b>: ${e.model||"none"}</div>
          <div><b>Category</b>: ${e.entity_category} · <b>Name</b>: ${e.name||"none"}</div>
          <div><b>Label names</b>: ${e.label_names.join(", ")||"none"}</div>
          <div><b>State</b>: ${e.state??"none"}</div>
        </ha-card>
        ${e.rules.length?e.rules.map(t=>o`<ha-card class="pad">
          <div class="row"><b>${t.name}</b>
            <span class="muted">${t.enabled?t.included?t.excluded?"matches, but excluded":"included":"not included":"disabled"}</span></div>
          ${t.actions.map(s=>o`<div>${this._typeName(s.type)}
            ${s.targets.length?o`→ ${s.targets.map(i=>this._targetName(s.type,i)).join(", ")}`:d}:
            <b class=${s.status==="applies"?"ok":"muted"}>${s.status}</b></div>`)}
        </ha-card>`):o`<p class="muted">No rules.</p>`}`:d}
    `}async _doExplain(e){if(this._explainEntity=e,!e){this._explain=null;return}await this._run(async()=>{this._explain=await this._ws({type:"propsense/explain",entity_id:e})})}_setSetting(e,t){this._settingsDraft={...this._settingsDraft,[e]:t}}_renderSettings(){let e=this._settingsDraft,t=[...new Set(Object.keys(this.hass.states).map(i=>i.split(".")[0]))].sort(),s=(i,a,r)=>o`<label class="check">
      <input type="checkbox" .checked=${!!e[i]} @change=${c=>this._setSetting(i,c.target.checked)} />
      <span>${a}${r?o`<div class="muted">${r}</div>`:d}</span>
    </label>`;return o`
      <div class="row">
        <h2>Settings</h2>
        <button class="primary" ?disabled=${this._busy} @click=${this._saveSettings}>Save</button>
      </div>
      <ha-card class="pad">
        <div class="field">
          <div class="label">Managed assistants</div>
          <p class="muted">For these, anything no rule selects is un-exposed, including entities ticked by hand.</p>
          ${this._data.assistants.map(i=>o`<label class="check">
            <input type="checkbox" .checked=${e.managed_assistants.includes(i.value)}
              @change=${a=>this._setSetting("managed_assistants",a.target.checked?[...new Set([...e.managed_assistants,i.value])]:e.managed_assistants.filter(r=>r!==i.value))} />
            ${i.label}</label>`)}
        </div>
        <div class="field">
          <div class="label">Blocked domains</div>
          <p class="muted">Never exposed, even if a rule lists them explicitly.</p>
          <ha-selector .hass=${this.hass}
            .selector=${{select:{multiple:!0,custom_value:!0,options:t}}}
            .value=${e.blocked_domains}
            @value-changed=${i=>this._setSetting("blocked_domains",i.detail.value||[])}></ha-selector>
        </div>
        <div class="field">
          <div class="label">Maximum exposed per assistant</div>
          <p class="muted">If a plan would exceed this, nothing changes and a repair issue is raised. 0 disables the guard.</p>
          <input type="number" min="0" .value=${String(e.max_exposed)}
            @input=${i=>this._setSetting("max_exposed",Math.max(0,parseInt(i.target.value||"0",10)))} />
        </div>
        ${s("inherit_device_labels","Entities inherit their device's labels")}
        ${s("inherit_area_labels","Entities inherit their area's labels")}
        ${s("dry_run","Dry run","Compute and report the plan without applying it.")}
        ${s("allow_external_data","Allow sending data off this instance","Warning: lets rules send entity data (numeric history) to the metrics URL below, and nowhere else. Nothing is sent until this is on and a rule uses it. There are no credentials: the endpoint should only accept posts from your network.")}
        <div class="field">
          <div class="label">Metrics URL</div>
          <div class="muted">The only address data is ever sent to (InfluxDB line protocol, for example a VictoriaMetrics /write endpoint). There is no default: set yours before allowing data to leave.</div>
          <input type="text" placeholder="https://metrics.example.com/write" .value=${e.metrics_url||""}
            @input=${i=>this._setSetting("metrics_url",i.target.value.trim())} />
        </div>
        ${s("allow_third_party_actions","Allow third-party actions","Warning: other integrations can register actions that change things beyond voice exposure, such as granting entities to other Home Assistant instances. Rules using them stay dormant until this is on. Only enable it for integrations you trust.")}
      </ha-card>
    `}async _saveSettings(){await this._run(async()=>{await this._ws({type:"propsense/settings/update",settings:this._settingsDraft}),await new Promise(e=>setTimeout(e,1500)),await this._load()})}static styles=H`
    :host { display: block; min-height: 100vh; background: var(--primary-background-color); color: var(--primary-text-color); font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif); }
    .toolbar { display: flex; align-items: center; height: 56px; padding: 0 16px; background: var(--app-header-background-color, var(--primary-color)); color: var(--app-header-text-color, #fff); }
    .title { font-size: 20px; margin-left: 8px; }
    .tabs { display: flex; gap: 4px; padding: 0 12px; border-bottom: 1px solid var(--divider-color); background: var(--card-background-color); overflow-x: auto; }
    .tab { background: none; border: none; border-bottom: 2px solid transparent; padding: 12px 14px; color: var(--secondary-text-color); font: inherit; cursor: pointer; }
    .tab.active { color: var(--primary-color); border-bottom-color: var(--primary-color); }
    .content { max-width: 1100px; margin: 0 auto; padding: 16px; box-sizing: border-box; }
    h2 { margin: 8px 0; font-weight: 500; } h3 { margin: 0 0 8px; font-weight: 500; }
    .row { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
    .muted { color: var(--secondary-text-color); font-size: 0.9em; }
    .warn-text { color: var(--warning-color, #b26a00); margin: 6px 0; }
    .ok { color: var(--success-color, #2e7d32); }
    .error { background: var(--error-color, #c62828); color: #fff; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; }
    .notice { padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; background: var(--secondary-background-color); }
    .notice.warn { border-left: 4px solid var(--warning-color, #ff9800); }
    .notice button { margin-left: 8px; }
    ha-card { display: block; margin-bottom: 12px; }
    .pad { padding: 16px; }
    .rule { padding: 14px 16px; }
    .rule.off { opacity: 0.6; }
    .rule-head { display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
    .rule-name { font-size: 1.1em; font-weight: 500; }
    .rule-actions { display: flex; align-items: center; gap: 8px; }
    .sel { margin-top: 8px; }
    .editor { display: grid; grid-template-columns: minmax(0, 3fr) minmax(0, 2fr); gap: 16px; }
    @media (max-width: 800px) { .editor { grid-template-columns: 1fr; } }
    .sticky { position: sticky; top: 8px; }
    .field { margin-bottom: 14px; }
    .label { font-weight: 500; margin-bottom: 4px; }
    .check { display: flex; align-items: flex-start; gap: 8px; margin: 10px 0; }
    input[type="text"], input[type="number"], select { width: 100%; box-sizing: border-box; padding: 10px; border-radius: 6px; border: 1px solid var(--divider-color); background: var(--card-background-color); color: var(--primary-text-color); font: inherit; }
    input[type="number"] { max-width: 160px; }
    button { padding: 8px 14px; border-radius: 18px; border: 1px solid var(--divider-color); background: var(--card-background-color); color: var(--primary-text-color); font: inherit; cursor: pointer; }
    button.primary { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: var(--primary-color); }
    button.danger { color: var(--error-color, #c62828); }
    button:disabled { opacity: 0.5; cursor: default; }
    .action { border: 1px solid var(--divider-color); border-radius: 8px; padding: 10px; margin-bottom: 10px; }
    .action .row select { flex: 1; }
    .big { font-size: 2em; font-weight: 500; }
    .entities { list-style: none; padding: 0; margin: 8px 0; max-height: 360px; overflow: auto; }
    .entities li { display: flex; justify-content: space-between; gap: 8px; padding: 4px 0; border-bottom: 1px solid var(--divider-color); }
    .loading { padding: 24px; }
    summary { cursor: pointer; font-weight: 500; }
    .summary { margin: 4px 0 0; padding-left: 18px; }
    .help { margin: -2px 0 6px; }
    .line.cond { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: 6px 0; }
    .line.cond select { width: auto; }
    .line.cond input.val { width: 110px; }
    .line.cond input.attr { width: 150px; }
    details.more { margin-top: 8px; }
    details.more > summary { margin-bottom: 8px; }
    .templates { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 12px; margin-bottom: 16px; }
    .template { text-align: left; border-radius: 12px; padding: 14px; }
    .template:hover { border-color: var(--primary-color); }
    .sentence { margin-top: 8px; }
    .sentence .line { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin: 8px 0; }
    .sentence select { width: auto; }
    .sentence input.small { width: 72px; }
    .sentence input[type="time"] { width: auto; padding: 8px; border-radius: 6px; border: 1px solid var(--divider-color); background: var(--card-background-color); color: var(--primary-text-color); font: inherit; }
    .chip { padding: 4px 10px; border-radius: 14px; text-transform: capitalize; }
    .chip.on { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: var(--primary-color); }
    .runtime { padding: 8px 0; border-bottom: 1px solid var(--divider-color); }
    .runtime:last-child { border-bottom: none; }
    .toast { position: fixed; left: 50%; bottom: 24px; transform: translateX(-50%); background: var(--primary-text-color); color: var(--card-background-color); padding: 10px 18px; border-radius: 20px; z-index: 10; box-shadow: 0 2px 8px rgba(0,0,0,.3); }
  `};customElements.define("propsense-panel",te);
/*! Bundled license information:

@lit/reactive-element/css-tag.js:
  (**
   * @license
   * Copyright 2019 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

@lit/reactive-element/reactive-element.js:
lit-html/lit-html.js:
lit-element/lit-element.js:
  (**
   * @license
   * Copyright 2017 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)

lit-html/is-server.js:
  (**
   * @license
   * Copyright 2022 Google LLC
   * SPDX-License-Identifier: BSD-3-Clause
   *)
*/
