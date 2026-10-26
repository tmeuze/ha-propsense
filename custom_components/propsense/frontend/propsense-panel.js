var M=globalThis,D=M.ShadowRoot&&(M.ShadyCSS===void 0||M.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,j=Symbol(),st=new WeakMap,S=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==j)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(D&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=st.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&st.set(e,t))}return t}toString(){return this.cssText}},it=n=>new S(typeof n=="string"?n:n+"",void 0,j),H=(n,...t)=>{let e=n.length===1?n[0]:t.reduce((s,i,a)=>s+(r=>{if(r._$cssResult$===!0)return r.cssText;if(typeof r=="number")return r;throw Error("Value passed to 'css' function must be a 'css' function result: "+r+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+n[a+1],n[0]);return new S(e,n,j)},at=(n,t)=>{if(D)n.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),i=M.litNonce;i!==void 0&&s.setAttribute("nonce",i),s.textContent=e.cssText,n.appendChild(s)}},I=D?n=>n:n=>n instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return it(e)})(n):n;var{is:Et,defineProperty:kt,getOwnPropertyDescriptor:Ct,getOwnPropertyNames:Tt,getOwnPropertySymbols:Nt,getPrototypeOf:Pt}=Object,L=globalThis,nt=L.trustedTypes,Rt=nt?nt.emptyScript:"",Ot=L.reactiveElementPolyfillSupport,E=(n,t)=>n,F={toAttribute(n,t){switch(t){case Boolean:n=n?Rt:null;break;case Object:case Array:n=n==null?n:JSON.stringify(n)}return n},fromAttribute(n,t){let e=n;switch(t){case Boolean:e=n!==null;break;case Number:e=n===null?null:Number(n);break;case Object:case Array:try{e=JSON.parse(n)}catch{e=null}}return e}},ot=(n,t)=>!Et(n,t),rt={attribute:!0,type:String,converter:F,reflect:!1,useDefault:!1,hasChanged:ot};Symbol.metadata??=Symbol("metadata"),L.litPropertyMetadata??=new WeakMap;var _=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=rt){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),i=this.getPropertyDescriptor(t,s,e);i!==void 0&&kt(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){let{get:i,set:a}=Ct(this.prototype,t)??{get(){return this[e]},set(r){this[e]=r}};return{get:i,set(r){let c=i?.call(this);a?.call(this,r),this.requestUpdate(t,c,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??rt}static _$Ei(){if(this.hasOwnProperty(E("elementProperties")))return;let t=Pt(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(E("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(E("properties"))){let e=this.properties,s=[...Tt(e),...Nt(e)];for(let i of s)this.createProperty(i,e[i])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,i]of e)this.elementProperties.set(s,i)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let i=this._$Eu(e,s);i!==void 0&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let i of s)e.unshift(I(i))}else t!==void 0&&e.push(I(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return at(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),i=this.constructor._$Eu(t,s);if(i!==void 0&&s.reflect===!0){let a=(s.converter?.toAttribute!==void 0?s.converter:F).toAttribute(e,s.type);this._$Em=t,a==null?this.removeAttribute(i):this.setAttribute(i,a),this._$Em=null}}_$AK(t,e){let s=this.constructor,i=s._$Eh.get(t);if(i!==void 0&&this._$Em!==i){let a=s.getPropertyOptions(i),r=typeof a.converter=="function"?{fromAttribute:a.converter}:a.converter?.fromAttribute!==void 0?a.converter:F;this._$Em=i;let c=r.fromAttribute(e,a.type);this[i]=c??this._$Ej?.get(i)??c,this._$Em=null}}requestUpdate(t,e,s,i=!1,a){if(t!==void 0){let r=this.constructor;if(i===!1&&(a=this[t]),s??=r.getPropertyOptions(t),!((s.hasChanged??ot)(a,e)||s.useDefault&&s.reflect&&a===this._$Ej?.get(t)&&!this.hasAttribute(r._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:i,wrapped:a},r){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,r??e??this[t]),a!==!0||r!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),i===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,a]of this._$Ep)this[i]=a;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[i,a]of s){let{wrapped:r}=a,c=this[i];r!==!0||this._$AL.has(i)||c===void 0||this.C(i,void 0,a,c)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};_.elementStyles=[],_.shadowRootOptions={mode:"open"},_[E("elementProperties")]=new Map,_[E("finalized")]=new Map,Ot?.({ReactiveElement:_}),(L.reactiveElementVersions??=[]).push("2.1.2");var G=globalThis,lt=n=>n,U=G.trustedTypes,dt=U?U.createPolicy("lit-html",{createHTML:n=>n}):void 0,_t="$lit$",v=`lit$${Math.random().toFixed(9).slice(2)}$`,gt="?"+v,Mt=`<${gt}>`,y=document,C=()=>y.createComment(""),T=n=>n===null||typeof n!="object"&&typeof n!="function",J=Array.isArray,Dt=n=>J(n)||typeof n?.[Symbol.iterator]=="function",z=`[ 	
\f\r]`,k=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,ct=/-->/g,ht=/>/g,$=RegExp(`>|${z}(?:([^\\s"'>=/]+)(${z}*=${z}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),pt=/'/g,ut=/"/g,vt=/^(?:script|style|textarea|title)$/i,Y=n=>(t,...e)=>({_$litType$:n,strings:t,values:e}),o=Y(1),Qt=Y(2),te=Y(3),x=Symbol.for("lit-noChange"),d=Symbol.for("lit-nothing"),mt=new WeakMap,b=y.createTreeWalker(y,129);function ft(n,t){if(!J(n)||!n.hasOwnProperty("raw"))throw Error("invalid template strings array");return dt!==void 0?dt.createHTML(t):t}var Lt=(n,t)=>{let e=n.length-1,s=[],i,a=t===2?"<svg>":t===3?"<math>":"",r=k;for(let c=0;c<e;c++){let l=n[c],h,u,p=-1,m=0;for(;m<l.length&&(r.lastIndex=m,u=r.exec(l),u!==null);)m=r.lastIndex,r===k?u[1]==="!--"?r=ct:u[1]!==void 0?r=ht:u[2]!==void 0?(vt.test(u[2])&&(i=RegExp("</"+u[2],"g")),r=$):u[3]!==void 0&&(r=$):r===$?u[0]===">"?(r=i??k,p=-1):u[1]===void 0?p=-2:(p=r.lastIndex-u[2].length,h=u[1],r=u[3]===void 0?$:u[3]==='"'?ut:pt):r===ut||r===pt?r=$:r===ct||r===ht?r=k:(r=$,i=void 0);let g=r===$&&n[c+1].startsWith("/>")?" ":"";a+=r===k?l+Mt:p>=0?(s.push(h),l.slice(0,p)+_t+l.slice(p)+v+g):l+v+(p===-2?c:g)}return[ft(n,a+(n[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},N=class n{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let a=0,r=0,c=t.length-1,l=this.parts,[h,u]=Lt(t,e);if(this.el=n.createElement(h,s),b.currentNode=this.el.content,e===2||e===3){let p=this.el.content.firstChild;p.replaceWith(...p.childNodes)}for(;(i=b.nextNode())!==null&&l.length<c;){if(i.nodeType===1){if(i.hasAttributes())for(let p of i.getAttributeNames())if(p.endsWith(_t)){let m=u[r++],g=i.getAttribute(p).split(v),O=/([.?@])?(.*)/.exec(m);l.push({type:1,index:a,name:O[2],strings:g,ctor:O[1]==="."?W:O[1]==="?"?V:O[1]==="@"?q:A}),i.removeAttribute(p)}else p.startsWith(v)&&(l.push({type:6,index:a}),i.removeAttribute(p));if(vt.test(i.tagName)){let p=i.textContent.split(v),m=p.length-1;if(m>0){i.textContent=U?U.emptyScript:"";for(let g=0;g<m;g++)i.append(p[g],C()),b.nextNode(),l.push({type:2,index:++a});i.append(p[m],C())}}}else if(i.nodeType===8)if(i.data===gt)l.push({type:2,index:a});else{let p=-1;for(;(p=i.data.indexOf(v,p+1))!==-1;)l.push({type:7,index:a}),p+=v.length-1}a++}}static createElement(t,e){let s=y.createElement("template");return s.innerHTML=t,s}};function w(n,t,e=n,s){if(t===x)return t;let i=s!==void 0?e._$Co?.[s]:e._$Cl,a=T(t)?void 0:t._$litDirective$;return i?.constructor!==a&&(i?._$AO?.(!1),a===void 0?i=void 0:(i=new a(n),i._$AT(n,e,s)),s!==void 0?(e._$Co??=[])[s]=i:e._$Cl=i),i!==void 0&&(t=w(n,i._$AS(n,t.values),i,s)),t}var B=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,i=(t?.creationScope??y).importNode(e,!0);b.currentNode=i;let a=b.nextNode(),r=0,c=0,l=s[0];for(;l!==void 0;){if(r===l.index){let h;l.type===2?h=new P(a,a.nextSibling,this,t):l.type===1?h=new l.ctor(a,l.name,l.strings,this,t):l.type===6&&(h=new K(a,this,t)),this._$AV.push(h),l=s[++c]}r!==l?.index&&(a=b.nextNode(),r++)}return b.currentNode=y,i}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},P=class n{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,i){this.type=2,this._$AH=d,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=w(this,t,e),T(t)?t===d||t==null||t===""?(this._$AH!==d&&this._$AR(),this._$AH=d):t!==this._$AH&&t!==x&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Dt(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==d&&T(this._$AH)?this._$AA.nextSibling.data=t:this.T(y.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,i=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=N.createElement(ft(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(e);else{let a=new B(i,this),r=a.u(this.options);a.p(e),this.T(r),this._$AH=a}}_$AC(t){let e=mt.get(t.strings);return e===void 0&&mt.set(t.strings,e=new N(t)),e}k(t){J(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,i=0;for(let a of t)i===e.length?e.push(s=new n(this.O(C()),this.O(C()),this,this.options)):s=e[i],s._$AI(a),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=lt(t).nextSibling;lt(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},A=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,i,a){this.type=1,this._$AH=d,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=a,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=d}_$AI(t,e=this,s,i){let a=this.strings,r=!1;if(a===void 0)t=w(this,t,e,0),r=!T(t)||t!==this._$AH&&t!==x,r&&(this._$AH=t);else{let c=t,l,h;for(t=a[0],l=0;l<a.length-1;l++)h=w(this,c[s+l],e,l),h===x&&(h=this._$AH[l]),r||=!T(h)||h!==this._$AH[l],h===d?t=d:t!==d&&(t+=(h??"")+a[l+1]),this._$AH[l]=h}r&&!i&&this.j(t)}j(t){t===d?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},W=class extends A{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===d?void 0:t}},V=class extends A{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==d)}},q=class extends A{constructor(t,e,s,i,a){super(t,e,s,i,a),this.type=5}_$AI(t,e=this){if((t=w(this,t,e,0)??d)===x)return;let s=this._$AH,i=t===d&&s!==d||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,a=t!==d&&(s===d||i);i&&this.element.removeEventListener(this.name,this,s),a&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},K=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){w(this,t)}};var Ut=G.litHtmlPolyfillSupport;Ut?.(N,P),(G.litHtmlVersions??=[]).push("3.3.3");var $t=(n,t,e)=>{let s=e?.renderBefore??t,i=s._$litPart$;if(i===void 0){let a=e?.renderBefore??null;s._$litPart$=i=new P(t.insertBefore(C(),a),a,void 0,e??{})}return i._$AI(n),i};var X=globalThis,f=class extends _{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=$t(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return x}};f._$litElement$=!0,f.finalized=!0,X.litElementHydrateSupport?.({LitElement:f});var jt=X.litElementPolyfillSupport;jt?.({LitElement:f});(X.litElementVersions??=[]).push("4.2.2");var R=[["labels","Labels"],["areas","Areas"],["floors","Floors"],["domains","Domains"],["devices","Devices"],["entities","Entities"],["groups","Groups"],["capabilities","Capabilities"],["integrations","Integrations"],["manufacturers","Manufacturers"],["models","Models"],["entity_categories","Entity categories"],["name_patterns","Name or entity id patterns"],["label_patterns","Label name patterns"],["states","Current state"],["conditions","Conditions on state or attributes"]],Z=["states","conditions"],Ht=["on","off","unavailable","unknown","open","closed","home","not_home","locked","unlocked","playing","idle","paused"],It=[["<","is below"],["<=","is at most"],[">","is above"],[">=","is at least"],["=","is"],["!=","is not"],["between","is between"]];function bt(n){let[t="state",e="<",...s]=String(n).trim().split(/\s+/),i=t==="state"?"state":"attr",a=t.startsWith("attr:")?t.slice(5):"";return e==="between"?{source:i,attr:a,op:e,a:s[0]||"",b:s[1]||""}:{source:i,attr:a,op:e,a:s.join(" "),b:""}}var yt=n=>(n.source==="state"||n.attr.trim())&&String(n.a).trim()&&(n.op!=="between"||String(n.b).trim()),Ft=n=>`${n.source==="state"?"state":`attr:${n.attr.trim()}`} ${n.op} ${n.op==="between"?`${String(n.a).trim()} ${String(n.b).trim()}`:String(n.a).trim()}`,xt=["integrations","manufacturers","models","entity_categories","name_patterns","label_patterns"],Q={integrations:"Where the entity comes from, for example hue or zha.",manufacturers:"Of the entity's device. Wildcards work: IKEA*.",models:"Of the entity's device. Wildcards work.",entity_categories:"Primary entities are the ones with no category. Config and diagnostic entities are the extras integrations add.",name_patterns:"Matches the entity id or its name, ignoring case. Use * for any text and ? for one character, for example switch.*_plug or *outlet*.",label_patterns:"Matches label names, ignoring case, for example Expose: * for every label that starts that way.",states:"The entity's state right now, for example on or unavailable. Any of the values will do.",conditions:"Matches if any of these hold. The rule re-checks whenever an entity's state changes across a condition."},zt=[{value:"primary",label:"Primary (no category)"},{value:"config",label:"Config"},{value:"diagnostic",label:"Diagnostic"}],wt=[{value:"onoff",label:"Light: on/off only"},{value:"brightness",label:"Light: brightness"},{value:"color_temp",label:"Light: white temperature"},{value:"color",label:"Light: color"},{value:"white",label:"Light: white channel"},{value:"position",label:"Cover: set position"},{value:"tilt",label:"Cover: set tilt"},{value:"speed",label:"Fan: speed"},{value:"oscillate",label:"Fan: oscillate"},{value:"direction",label:"Fan: direction"},{value:"preset",label:"Fan: preset modes"},{value:"heat",label:"Climate: heat"},{value:"cool",label:"Climate: cool"},{value:"heat_cool",label:"Climate: heat/cool"},{value:"auto",label:"Climate: auto"},{value:"dry",label:"Climate: dry"},{value:"fan_only",label:"Climate: fan only"},{value:"target_temp",label:"Climate: target temperature"}],Bt=["device_classes"],Wt=26,Vt=[["rules","Rules"],["status","Status"],["explain","Explain"],["settings","Settings"]],qt=(n,t=0)=>({hours:n,minutes:t,seconds:0}),Kt=[{id:"auto_off",title:"Auto-off timer",text:"Turn outlets off after they have been on for a while. Survives restarts and respects manual switching.",make:()=>({name:"Auto-off outlets",include:{domains:["switch"]},actions:[{type:"schedule",config:{trigger:"state_for",state:"on",do:"turn_off",duration:qt(3)}}]})},{id:"sunset_on",title:"Lights on at sunset",text:"Turn lights on at sunset, with an optional offset.",make:()=>({name:"Lights on at sunset",include:{domains:["light"]},actions:[{type:"schedule",config:{trigger:"sun",event:"sunset",offset_minutes:0,do:"turn_on",catch_up_minutes:30}}]})},{id:"night_off",title:"Lights off at night",text:"Turn lights off at a set time of day.",make:()=>({name:"Lights off at night",include:{domains:["light"]},actions:[{type:"schedule",config:{trigger:"time",at:"23:00:00",do:"turn_off",catch_up_minutes:0}}]})},{id:"expose",title:"Expose to a voice assistant",text:"Let Assist, Alexa or Google see the entities with a label.",make:()=>({name:"Voice assistant exposure",include:{},actions:[{type:"expose",config:{assistants:["conversation"]}}]})},{id:"group",title:"Keep a group in sync",text:"Fill a group with the entities a rule selects, for example every light with white temperature.",make:()=>({name:"Dynamic group",include:{},actions:[{type:"group",config:{create_name:"",group_type:"light"}}]})},{id:"metrics",title:"Ship numeric history",text:"Send the numeric history of entities (by label, integration, name\u2026) to your metrics endpoint. Needs the permission in Settings.",make:()=>({name:"Ship metrics",include:{},actions:[{type:"metrics",config:{min_interval_seconds:60,include_booleans:!1,tag_area:!0,tag_device_class:!0,tag_unit:!0,max_entities:200}}]})},{id:"blank",title:"Start from scratch",text:"An empty rule.",make:()=>({})}],tt=()=>Object.fromEntries([...R.map(([n])=>n),...Bt].map(n=>[n,[]])),At=()=>({name:"",enabled:!0,include:tt(),exclude:tt(),actions:[{type:"expose",config:{assistants:["conversation"]}}]}),St=n=>!Object.values(n||{}).some(t=>t&&t.length);async function Gt(){try{if(customElements.get("ha-selector")&&customElements.get("ha-form"))return;await(await(await window.loadCardHelpers?.())?.createCardElement({type:"entities",entities:[]}))?.constructor?.getConfigElement?.()}catch{}}var et=class extends f{static properties={hass:{attribute:!1},narrow:{type:Boolean},panel:{attribute:!1},_tab:{state:!0},_data:{state:!0},_error:{state:!0},_busy:{state:!0},_editing:{state:!0},_preview:{state:!0},_applyResult:{state:!0},_explain:{state:!0},_explainEntity:{state:!0},_settingsDraft:{state:!0},_showAll:{state:!0},_choosing:{state:!0},_toastMsg:{state:!0}};constructor(){super(),this._tab="rules",this._data=null,this._error="",this._busy=!1,this._editing=null,this._preview=null,this._applyResult=null,this._explain=null,this._explainEntity="",this._settingsDraft=null,this._showAll=!1,this._choosing=!1,this._toastMsg="",this._previewTimer=null}async connectedCallback(){super.connectedCallback(),await Gt(),await Promise.all([this._load(),this._loadNames()])}_ws(t){return this.hass.callWS(t)}async _load(){try{this._data=await this._ws({type:"propsense/overview"}),this._settingsDraft={...this._data.settings},this._error=""}catch(t){this._error=t.message||String(t)}}_toast(t){this._toastMsg=t,clearTimeout(this._toastTimer),this._toastTimer=setTimeout(()=>this._toastMsg="",3500)}_rel(t){let e=new Date(t).getTime()-Date.now(),s=Math.abs(e),i=Math.round(s/6e4),a=i>=60?`${Math.floor(i/60)} h ${i%60} min`:`${i} min`;return e>=0?`in ${a}`:`${a} ago (waiting)`}async _run(t){this._busy=!0;try{await t(),this._error=""}catch(e){this._error=e.message||String(e)}finally{this._busy=!1}}async _loadNames(){this._names={labels:{},areas:{},floors:{}};let t=[["labels","config/label_registry/list","label_id"],["areas","config/area_registry/list","area_id"],["floors","config/floor_registry/list","floor_id"]];await Promise.all(t.map(async([e,s,i])=>{try{for(let a of await this._ws({type:s}))this._names[e][a[i]]=a.name}catch{}})),this.requestUpdate()}_labelName(t){return this._names?.labels?.[t]??this.hass.labels?.[t]?.name??t}_areaName(t){return this._names?.areas?.[t]??this.hass.areas?.[t]?.name??t}_floorName(t){return this._names?.floors?.[t]??this.hass.floors?.[t]?.name??t}_deviceName(t){let e=this.hass.devices?.[t];return e?.name_by_user||e?.name||t}_entityName(t){return this.hass.states?.[t]?.attributes?.friendly_name||t}_valueName(t,e){switch(t){case"labels":return this._labelName(e);case"areas":return this._areaName(e);case"floors":return this._floorName(e);case"devices":return this._deviceName(e);case"capabilities":return wt.find(s=>s.value===e)?.label??e;case"entities":case"groups":return this._entityName(e);default:return e}}_targetName(t,e){let s=this._data?.assistants?.find(i=>i.value===e);return t==="expose"&&s?s.label:e}_typeName(t){return this._data?.actions?.find(e=>e.type===t)?.name||t}_summarise(t){let e=R.filter(([s])=>t?.[s]?.length).map(([s,i])=>`${i}: ${t[s].map(a=>this._valueName(s,a)).join(", ")}`);return e.length?e.join(" \xB7 "):""}_countFor(t){let e=this._data?.last?.rules?.[t.name];return e===void 0?"\u2013":e}async _toggle(t){await this._run(async()=>{await this._ws({type:"propsense/rule/save",rule:{...t,enabled:!t.enabled}}),await this._applyAfterChange(),this._toast(t.enabled?`Disabled \u201C${t.name}\u201D`:`Enabled \u201C${t.name}\u201D`)})}async _delete(t){confirm(`Delete the rule "${t.name}"?`)&&await this._run(async()=>{await this._ws({type:"propsense/rule/delete",rule_id:t.id}),await this._applyAfterChange()})}async _applyAfterChange(){await this._ws({type:"propsense/apply",dry_run:!1}),await this._load()}_edit(t){this._choosing=!1,this._condDrafts=null,this._editing={...At(),...JSON.parse(JSON.stringify(t||At()))};for(let e of["include","exclude"])this._editing[e]={...tt(),...this._editing[e]};this._preview=null,this._showAll=!1,this._schedulePreview()}_setEditing(t){this._editing={...this._editing,...t},this._schedulePreview()}_setSelector(t,e,s){this._setEditing({[t]:{...this._editing[t],[e]:s||[]}})}_schedulePreview(){clearTimeout(this._previewTimer),this._previewTimer=setTimeout(()=>this._runPreview(),400)}async _runPreview(){if(!this._editing)return;let t=this._cleanRule();t.name||(t.name="(draft)");try{this._preview=await this._ws({type:"propsense/preview",rule:t})}catch(e){this._preview={error:e.message||String(e)}}}_cleanRule(){let{id:t,name:e,enabled:s,include:i,exclude:a,actions:r}=this._editing;return{...t?{id:t}:{},name:(e||"").trim(),enabled:s,include:i,exclude:a,actions:r}}async _save(){let t=this._cleanRule();if(!t.name){this._error="Give the rule a name.";return}await this._run(async()=>{await this._ws({type:"propsense/rule/save",rule:t}),this._editing=null,await this._applyAfterChange(),this._toast(`Saved \u201C${t.name}\u201D`)})}_addAction(){let t=this._data.actions.find(s=>s.available)?.type||this._data.actions[0].type,e=this._defaultConfig(t);this._setEditing({actions:[...this._editing.actions,{type:t,config:e}]})}_defaultConfig(t){let e=this._data.actions.find(s=>s.type===t)?.schema||[];return Object.fromEntries(e.filter(s=>s.default!==void 0).map(s=>[s.name,s.default]))}_setAction(t,e){let s=this._editing.actions.map((i,a)=>t===a?{...i,...e}:i);this._setEditing({actions:s})}_removeAction(t){this._setEditing({actions:this._editing.actions.filter((e,s)=>s!==t)})}render(){return!this._data&&!this._error?o`<div class="loading">Loading…</div>`:o`
      <div class="toolbar">
        ${this.narrow?o`<ha-menu-button .hass=${this.hass} .narrow=${this.narrow}></ha-menu-button>`:d}
        <div class="title">PropSense</div>
      </div>
      <div class="tabs">
        ${Vt.map(([t,e])=>o`<button
            class="tab ${this._tab===t?"active":""}"
            @click=${()=>this._tab=t}
          >${e}</button>`)}
      </div>
      ${this._toastMsg?o`<div class="toast">${this._toastMsg}</div>`:d}
      <div class="content">
        ${this._error?o`<div class="error">${this._error}</div>`:d}
        ${this._data?this._renderTab():d}
      </div>
    `}_renderTab(){if(this._editing&&this._tab==="rules")return this._renderEditor();switch(this._tab){case"status":return this._renderStatus();case"explain":return this._renderExplain();case"settings":return this._renderSettings();default:return this._renderRules()}}_renderRules(){let{rules:t,settings:e}=this._data;return o`
      ${!t.length&&!e.dry_run?o`<div class="notice warn">
            <b>Start with a dry run.</b> Rules are the single source of truth: with no rules,
            everything an assistant PropSense manages can see is un-exposed on the next apply.
            <button @click=${()=>this._setDryRun(!0)}>Turn on dry run</button>
          </div>`:d}
      ${e.dry_run?o`<div class="notice">
            Dry run is on: rules are evaluated but nothing is applied.
            <button @click=${()=>this._setDryRun(!1)}>Turn off</button>
          </div>`:d}
      <div class="row">
        <h2>Rules</h2>
        <button class="primary" @click=${()=>this._choosing=!this._choosing}>Add rule</button>
      </div>
      ${this._choosing?this._renderChooser():d}
      ${t.length?t.map(s=>this._renderRuleCard(s)):o`<p class="muted">No rules yet. A rule selects entities, for example everything labelled
            “Expose: Voice”, and applies actions such as exposing them to Assist.</p>`}
    `}_renderChooser(){return o`<div class="templates">
      ${Kt.map(t=>o`<button class="template" @click=${()=>this._edit(t.make())}>
          <div class="rule-name">${t.title}</div>
          <div class="muted">${t.text}</div>
        </button>`)}
    </div>`}async _setDryRun(t){await this._run(async()=>{await this._ws({type:"propsense/settings/update",settings:{dry_run:t}}),await new Promise(e=>setTimeout(e,1500)),await this._load()})}_renderRuleCard(t){let e=this._summarise(t.include),s=this._summarise(t.exclude),i=this._data.last?.dormant?.[t.name];return o`<ha-card class="rule ${t.enabled?"":"off"}">
      <div class="rule-head">
        <div>
          <div class="rule-name">${t.name}</div>
          <div class="muted">${this._countFor(t)} ${this._countFor(t)===1?"entity":"entities"}</div>
          <ul class="summary">
            ${(this._data.summaries?.[t.id]||[]).map(a=>o`<li>${a}</li>`)}
          </ul>
        </div>
        <div class="rule-actions">
          <label class="switch" title="Enable or disable">
            <input type="checkbox" .checked=${t.enabled} @change=${()=>this._toggle(t)} />
            ${t.enabled?"On":"Off"}
          </label>
          <button @click=${()=>this._edit(t)}>Edit</button>
          <button class="danger" @click=${()=>this._delete(t)}>Delete</button>
        </div>
      </div>
      <div class="sel">${e||o`<span class="warn-text">Selects nothing (no include fields).</span>`}</div>
      ${s?o`<div class="sel muted">Except: ${s}</div>`:d}
      ${i?o`<div class="warn-text">Dormant action: ${i.join(", ")}. Needs the provider, and the matching permission in Settings.</div>`:d}
    </ha-card>`}_selectorFor(t){switch(t){case"labels":return{label:{multiple:!0}};case"areas":return{area:{multiple:!0}};case"floors":return{floor:{multiple:!0}};case"devices":return{device:{multiple:!0}};case"entities":case"groups":return{entity:{multiple:!0}};case"capabilities":return{select:{multiple:!0,options:wt}};case"entity_categories":return{select:{multiple:!0,options:zt}};case"integrations":case"manufacturers":case"models":return{select:{multiple:!0,custom_value:!0,options:this._data?.choices?.[t]||[]}};case"name_patterns":case"label_patterns":return{select:{multiple:!0,custom_value:!0,options:[]}};case"states":return{select:{multiple:!0,custom_value:!0,options:Ht}};default:return{select:{multiple:!0,custom_value:!0,options:[...new Set(Object.keys(this.hass.states).map(s=>s.split(".")[0]))].sort()}}}}_renderSelectorFields(t){let e=this._editing[t],s=([h,u])=>o`<div class="field">
      <div class="label">${u}</div>
      ${Q[h]?o`<div class="muted help">${Q[h]}</div>`:d}
      <ha-selector
        .hass=${this.hass}
        .selector=${this._selectorFor(h)}
        .value=${e[h]||[]}
        @value-changed=${p=>this._setSelector(t,h,p.detail.value)}
      ></ha-selector>
    </div>`,i=R.filter(([h])=>!xt.includes(h)&&!Z.includes(h)),a=R.filter(([h])=>xt.includes(h)),r=a.some(([h])=>e[h]?.length),c=Z.some(h=>e[h]?.length),l=([h,u])=>h==="conditions"?this._renderConditions(t,u):s([h,u]);return o`${i.map(s)}
      <details class="more" ?open=${r}>
        <summary>More filters: integration, manufacturer, name patterns…</summary>
        ${a.map(s)}
      </details>
      <details class="more" ?open=${c}>
        <summary>Current state and attributes: battery below 20%, currently on…</summary>
        ${R.filter(([h])=>Z.includes(h)).map(l)}
      </details>`}_condRows(t){return this._condDrafts||(this._condDrafts={include:(this._editing.include.conditions||[]).map(bt),exclude:(this._editing.exclude.conditions||[]).map(bt)}),this._condDrafts[t]}_setCondRows(t,e){this._condDrafts[t]=e,this._setSelector(t,"conditions",e.filter(yt).map(Ft))}_renderConditions(t,e){let s=this._condRows(t),i=(a,r)=>this._setCondRows(t,s.map((c,l)=>a===l?{...c,...r}:c));return o`<div class="field">
      <div class="label">${e}</div>
      <div class="muted help">${Q.conditions}</div>
      ${s.map((a,r)=>o`<div class="line cond">
        <select @change=${c=>i(r,{source:c.target.value})}>
          <option value="state" ?selected=${a.source==="state"}>State</option>
          <option value="attr" ?selected=${a.source==="attr"}>Attribute</option>
        </select>
        ${a.source==="attr"?o`<input type="text" class="attr" placeholder="battery_level" .value=${a.attr}
              @input=${c=>i(r,{attr:c.target.value})} />`:d}
        <select @change=${c=>i(r,{op:c.target.value})}>
          ${It.map(([c,l])=>o`<option value=${c} ?selected=${a.op===c}>${l}</option>`)}
        </select>
        <input type="text" class="val" .value=${a.a} placeholder=${a.op==="between"?"from":"value"}
          @input=${c=>i(r,{a:c.target.value})} />
        ${a.op==="between"?o`<span>and</span><input type="text" class="val" .value=${a.b} placeholder="to"
              @input=${c=>i(r,{b:c.target.value})} />`:d}
        <button class="danger" type="button" @click=${()=>this._setCondRows(t,s.filter((c,l)=>l!==r))}>Remove</button>
        ${yt(a)?d:o`<span class="warn-text">Incomplete: not used yet.</span>`}
      </div>`)}
      <button type="button" @click=${()=>this._setCondRows(t,[...s,{source:"state",attr:"",op:"<",a:"",b:""}])}>Add condition</button>
    </div>`}_renderEditor(){let t=this._editing;return o`
      <div class="row">
        <h2>${t.id?"Edit rule":"New rule"}</h2>
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
                .value=${t.name}
                placeholder="For example: Voice assistant"
                @input=${e=>this._setEditing({name:e.target.value})}
              />
            </div>
            <label class="check">
              <input type="checkbox" .checked=${t.enabled}
                @change=${e=>this._setEditing({enabled:e.target.checked})} />
              Enabled
            </label>
          </ha-card>

          <ha-card class="pad">
            <h3>1 · What does it apply to?</h3>
            <p class="muted">Every field you fill in must match (and); within a field any value will do (or). The live preview shows what is selected.</p>
            ${this._renderSelectorFields("include")}
          </ha-card>

          <ha-card class="pad">
            <details ?open=${!St(t.exclude)}>
              <summary>Exclude (optional)</summary>
              <p class="muted">Entities matching all the fields you fill in here are removed from this rule.</p>
              ${this._renderSelectorFields("exclude")}
            </details>
          </ha-card>

          <ha-card class="pad">
            <div class="row"><h3>2 · What should happen?</h3>
              <button @click=${this._addAction}>Add action</button></div>
            ${t.actions.length?t.actions.map((e,s)=>this._renderAction(e,s)):o`<p class="warn-text">No actions: this rule does nothing.</p>`}
          </ha-card>
        </div>
        <div class="col">${this._renderPreview()}</div>
      </div>
    `}_renderAction(t,e){let s=this._data.actions,i=s.find(r=>r.type===t.type),a=r=>this._labels[r.name]??r.name.replaceAll("_"," ");return o`<div class="action">
      <div class="row">
        <select @change=${r=>this._setAction(e,{type:r.target.value,config:this._defaultConfig(r.target.value)})}>
          ${s.map(r=>o`<option value=${r.type} ?selected=${r.type===t.type} ?disabled=${!r.available&&r.type!==t.type}>
              ${r.name}${r.available?"":r.requires==="external_data"?" (allow sending data in Settings)":" (enable third-party actions)"}
            </option>`)}
          ${i?d:o`<option selected>${t.type} (not installed)</option>`}
        </select>
        <button class="danger" @click=${()=>this._removeAction(e)}>Remove</button>
      </div>
      ${t.type==="schedule"?this._renderSchedule(t,e):d}
      ${i&&t.type!=="schedule"?o`${i.available?d:o`<div class="warn-text">${i.requires==="external_data"?"Dormant: allow sending data off this instance in Settings first. Nothing is sent until you do.":"Dormant until third-party actions are allowed in Settings."}</div>`}
          <ha-form
            .hass=${this.hass}
            .schema=${i.schema}
            .data=${t.config}
            .computeLabel=${a}
            @value-changed=${r=>this._setAction(e,{config:r.detail.value})}
          ></ha-form>`:t.type==="schedule"||i?d:o`<div class="warn-text">This action type is not installed, so the rule is dormant.</div>`}
    </div>`}_renderSchedule(t,e){let s={trigger:"state_for",do:"turn_off",state:"on",event:"sunset",offset_minutes:0,catch_up_minutes:0,days:[],...t.config},i=l=>this._setAction(e,{config:{...s,...l}}),a={hours:0,minutes:0,seconds:0,...s.duration||{}},r=l=>Math.max(0,parseInt(l||"0",10)||0),c=["mon","tue","wed","thu","fri","sat","sun"];return o`<div class="sentence">
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
    </div>`}_labels={assistants:"Expose to",group:"Existing group (to edit)",create_name:"Or create a group named",group_type:"Type of group to create",min_interval_seconds:"Seconds between points per entity (at least)",include_booleans:"Also send on/off as 1/0",tag_area:"Tag points with the area",tag_device_class:"Tag points with the device class",tag_unit:"Tag points with the unit",max_entities:"Most entities this rule may ship"};_renderPreview(){let t=this._preview,e=this._editing;return o`<ha-card class="pad sticky">
      <h3>Live preview</h3>
      ${St(e.include)?o`<p class="warn-text">Selects nothing: fill in at least one include field.</p>`:d}
      ${t?t.error?o`<p class="warn-text">${t.error}</p>`:this._renderPreviewBody(t):o`<p class="muted">Working…</p>`}
    </ha-card>`}_renderPreviewBody(t){let e=t.draft,s=e?.entities||[],i=this._showAll?s:s.slice(0,25),a=this._editing.actions.some(r=>r.type==="expose");return o`
      <div class="big">${e?.count??0} <span class="muted">entities selected</span></div>
      ${a?o`<div class="muted">About ${(e?.count??0)*Wt} prompt tokens if exposed to an LLM agent.</div>`:d}
      ${Object.entries(t.assistants||{}).map(([r,c])=>c.refused?o`<div class="warn-text">${this._targetName("expose",r)}: over the size limit, nothing would change.</div>`:d)}
      ${e?.skipped&&Object.keys(e.skipped).length?o`<div class="warn-text">Skipped: ${Object.entries(e.skipped).map(([r,c])=>`${r} (${c})`).join("; ")}</div>`:d}
      <ul class="entities">
        ${i.map(r=>o`<li><span>${r.name}</span> <span class="muted">${r.entity_id}</span></li>`)}
      </ul>
      ${s.length>i.length?o`<button @click=${()=>this._showAll=!0}>Show all ${s.length}</button>`:d}
    `}_renderStatus(){let t=this._data.last,e=this._applyResult||t;return o`
      <div class="row">
        <h2>Status</h2>
        <div>
          <button ?disabled=${this._busy} @click=${()=>this._apply(!0)}>Dry run</button>
          <button class="primary" ?disabled=${this._busy} @click=${()=>this._apply(!1)}>Apply now</button>
        </div>
      </div>
      ${this._data.settings.dry_run?o`<div class="notice">Dry run is on: “Apply now” changes nothing, and timers and schedules don't fire.</div>`:d}
      ${this._renderRuntime()}
      ${e?o`
            <p class="muted">${e.dry_run?"Dry run":"Last applied"} ${new Date(e.at).toLocaleString()}</p>
            ${this._renderTargets("expose",e.assistants)}
            ${Object.entries(e.actions||{}).map(([s,i])=>this._renderTargets(s,i))}
            ${Object.keys(e.dormant||{}).length?o`<div class="notice warn">Dormant rules: ${Object.entries(e.dormant).map(([s,i])=>`${s} (${i.join(", ")})`).join("; ")}</div>`:d}
            ${Object.keys(e.blocked||{}).length?o`<div class="notice">Skipped (matched a rule but never applied): ${Object.entries(e.blocked).map(([s,i])=>`${s} (${i})`).join("; ")}</div>`:d}
          `:o`<p class="muted">Nothing has been applied yet.</p>`}
    `}_renderMetrics(){let t=this._data.runtime?.metrics;return!t||!t.targets?.length?d:o`<ha-card class="pad">
      <h3>Metrics shipping</h3>
      ${t.url?o`<div class="muted">Sending to <code>${t.url}</code> and nowhere else.</div>`:d}
      ${t.url?d:o`<div class="warn-text">No Metrics URL is set. Set one in Settings; nothing is sent until then.</div>`}
      ${t.targets.map(e=>o`<div>${e.label} · ${e.entities} entities</div>`)}
      <div>Sent ${t.sent} points · waiting to send ${t.buffered}${t.dropped?o` · <span class="warn-text">dropped ${t.dropped}</span>`:d}</div>
      ${t.last_error?o`<div class="warn-text">Last send failed: ${t.last_error}. Points wait in memory and are retried every 30 seconds.</div>`:t.last_success?o`<div class="muted">Last success ${new Date(t.last_success).toLocaleString()}</div>`:d}
    </ha-card>`}_renderRuntime(){let t=this._data.runtime?.schedule?.schedules||[];return t.length?o`${this._renderMetrics()}<ha-card class="pad">
      <h3>Timers and schedules</h3>
      ${t.map(e=>o`<div class="runtime">
        <div><b>${e.label}</b> <span class="muted">· ${e.entities.length} entities</span></div>
        ${e.timers?.length?o`<ul class="summary">${e.timers.map(s=>o`<li>${this._entityName(s.entity_id)}: ${this._rel(s.due)}</li>`)}</ul>`:e.trigger==="state_for"?o`<div class="muted">No running timers: none of them is in that state.</div>`:d}
        ${e.next?o`<div class="muted">Next run ${new Date(e.next).toLocaleString()} (${this._rel(e.next)})</div>`:d}
      </div>`)}
    </ha-card>`:this._renderMetrics()}_renderTargets(t,e){return Object.entries(e||{}).map(([s,i])=>o`<ha-card class="pad">
        <div class="row">
          <div><b>${this._typeName(t)}</b> → ${i.label||this._targetName(t,s)}</div>
          <div>${i.count} entities${t==="expose"?o` · ~${i.estimated_tokens} tokens`:d}</div>
        </div>
        ${i.refused?o`<div class="warn-text">Refused: over the size limit. Nothing was changed.</div>`:d}
        ${i.error?o`<div class="warn-text">Error: ${i.error}</div>`:d}
        ${i.added?.length?o`<div>Adds ${i.added.length}: <span class="muted">${i.added.join(", ")}</span></div>`:d}
        ${i.removed?.length?o`<div>Removes ${i.removed.length}: <span class="muted">${i.removed.join(", ")}</span></div>`:d}
      </ha-card>`)}async _apply(t){await this._run(async()=>{let e=await this._ws({type:"propsense/apply",dry_run:t});this._applyResult=t?e:null,await this._load()})}_renderExplain(){let t=this._explain;return o`
      <h2>Explain an entity</h2>
      <p class="muted">Pick an entity to see which rules select it, and why not.</p>
      <ha-selector
        .hass=${this.hass}
        .selector=${{entity:{}}}
        .value=${this._explainEntity}
        @value-changed=${e=>this._doExplain(e.detail.value)}
      ></ha-selector>
      ${t&&!t.found?o`<p class="warn-text">PropSense doesn't know this entity (it may be disabled).</p>`:d}
      ${t?.found?o`
        <ha-card class="pad">
          <div><b>Labels</b>: ${t.labels.map(e=>this._labelName(e)).join(", ")||"none"}</div>
          <div><b>Area</b>: ${t.area_id?this._areaName(t.area_id):"none"}
            · <b>Floor</b>: ${t.floor_id?this._floorName(t.floor_id):"none"}</div>
          <div><b>Groups</b>: ${t.groups.map(e=>this._entityName(e)).join(", ")||"none"}</div>
          <div><b>Capabilities</b>: ${t.capabilities.map(e=>this._valueName("capabilities",e)).join(", ")||"none"}</div>
          <div><b>Integration</b>: ${t.integration||"none"}
            · <b>Manufacturer</b>: ${t.manufacturer||"none"} · <b>Model</b>: ${t.model||"none"}</div>
          <div><b>Category</b>: ${t.entity_category} · <b>Name</b>: ${t.name||"none"}</div>
          <div><b>Label names</b>: ${t.label_names.join(", ")||"none"}</div>
          <div><b>State</b>: ${t.state??"none"}</div>
        </ha-card>
        ${t.rules.length?t.rules.map(e=>o`<ha-card class="pad">
          <div class="row"><b>${e.name}</b>
            <span class="muted">${e.enabled?e.included?e.excluded?"matches, but excluded":"included":"not included":"disabled"}</span></div>
          ${e.actions.map(s=>o`<div>${this._typeName(s.type)}
            ${s.targets.length?o`→ ${s.targets.map(i=>this._targetName(s.type,i)).join(", ")}`:d}:
            <b class=${s.status==="applies"?"ok":"muted"}>${s.status}</b></div>`)}
        </ha-card>`):o`<p class="muted">No rules.</p>`}`:d}
    `}async _doExplain(t){if(this._explainEntity=t,!t){this._explain=null;return}await this._run(async()=>{this._explain=await this._ws({type:"propsense/explain",entity_id:t})})}_setSetting(t,e){this._settingsDraft={...this._settingsDraft,[t]:e}}_renderSettings(){let t=this._settingsDraft,e=[...new Set(Object.keys(this.hass.states).map(i=>i.split(".")[0]))].sort(),s=(i,a,r)=>o`<label class="check">
      <input type="checkbox" .checked=${!!t[i]} @change=${c=>this._setSetting(i,c.target.checked)} />
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
            <input type="checkbox" .checked=${t.managed_assistants.includes(i.value)}
              @change=${a=>this._setSetting("managed_assistants",a.target.checked?[...new Set([...t.managed_assistants,i.value])]:t.managed_assistants.filter(r=>r!==i.value))} />
            ${i.label}</label>`)}
        </div>
        <div class="field">
          <div class="label">Blocked domains</div>
          <p class="muted">Never exposed, even if a rule lists them explicitly.</p>
          <ha-selector .hass=${this.hass}
            .selector=${{select:{multiple:!0,custom_value:!0,options:e}}}
            .value=${t.blocked_domains}
            @value-changed=${i=>this._setSetting("blocked_domains",i.detail.value||[])}></ha-selector>
        </div>
        <div class="field">
          <div class="label">Maximum exposed per assistant</div>
          <p class="muted">If a plan would exceed this, nothing changes and a repair issue is raised. 0 disables the guard.</p>
          <input type="number" min="0" .value=${String(t.max_exposed)}
            @input=${i=>this._setSetting("max_exposed",Math.max(0,parseInt(i.target.value||"0",10)))} />
        </div>
        ${s("inherit_device_labels","Entities inherit their device's labels")}
        ${s("inherit_area_labels","Entities inherit their area's labels")}
        ${s("dry_run","Dry run","Compute and report the plan without applying it.")}
        ${s("allow_external_data","Allow sending data off this instance","Warning: lets rules send entity data (numeric history) to the metrics URL below, and nowhere else. Nothing is sent until this is on and a rule uses it. There are no credentials: the endpoint should only accept posts from your network.")}
        <div class="field">
          <div class="label">Metrics URL</div>
          <div class="muted">The only address data is ever sent to (InfluxDB line protocol, for example a VictoriaMetrics /write endpoint). There is no default: set yours before allowing data to leave.</div>
          <input type="text" placeholder="https://metrics.example.com/write" .value=${t.metrics_url||""}
            @input=${i=>this._setSetting("metrics_url",i.target.value.trim())} />
        </div>
        ${s("allow_third_party_actions","Allow third-party actions","Warning: other integrations can register actions that change things beyond voice exposure, such as granting entities to other Home Assistant instances. Rules using them stay dormant until this is on. Only enable it for integrations you trust.")}
      </ha-card>
    `}async _saveSettings(){await this._run(async()=>{await this._ws({type:"propsense/settings/update",settings:this._settingsDraft}),await new Promise(t=>setTimeout(t,1500)),await this._load()})}static styles=H`
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
  `};customElements.define("propsense-panel",et);
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
