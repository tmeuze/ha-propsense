var T=globalThis,j=T.ShadowRoot&&(T.ShadyCSS===void 0||T.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,M=Symbol(),tt=new WeakMap,E=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==M)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o,e=this.t;if(j&&t===void 0){let s=e!==void 0&&e.length===1;s&&(t=tt.get(e)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&tt.set(e,t))}return t}toString(){return this.cssText}},et=a=>new E(typeof a=="string"?a:a+"",void 0,M),H=(a,...t)=>{let e=a.length===1?a[0]:t.reduce((s,i,n)=>s+(r=>{if(r._$cssResult$===!0)return r.cssText;if(typeof r=="number")return r;throw Error("Value passed to 'css' function must be a 'css' function result: "+r+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+a[n+1],a[0]);return new E(e,a,M)},st=(a,t)=>{if(j)a.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of t){let s=document.createElement("style"),i=T.litNonce;i!==void 0&&s.setAttribute("nonce",i),s.textContent=e.cssText,a.appendChild(s)}},L=j?a=>a:a=>a instanceof CSSStyleSheet?(t=>{let e="";for(let s of t.cssRules)e+=s.cssText;return et(e)})(a):a;var{is:ft,defineProperty:yt,getOwnPropertyDescriptor:bt,getOwnPropertyNames:xt,getOwnPropertySymbols:wt,getPrototypeOf:At}=Object,U=globalThis,it=U.trustedTypes,Et=it?it.emptyScript:"",St=U.reactiveElementPolyfillSupport,S=(a,t)=>a,z={toAttribute(a,t){switch(t){case Boolean:a=a?Et:null;break;case Object:case Array:a=a==null?a:JSON.stringify(a)}return a},fromAttribute(a,t){let e=a;switch(t){case Boolean:e=a!==null;break;case Number:e=a===null?null:Number(a);break;case Object:case Array:try{e=JSON.parse(a)}catch{e=null}}return e}},nt=(a,t)=>!ft(a,t),at={attribute:!0,type:String,converter:z,reflect:!1,useDefault:!1,hasChanged:nt};Symbol.metadata??=Symbol("metadata"),U.litPropertyMetadata??=new WeakMap;var m=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=at){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){let s=Symbol(),i=this.getPropertyDescriptor(t,s,e);i!==void 0&&yt(this.prototype,t,i)}}static getPropertyDescriptor(t,e,s){let{get:i,set:n}=bt(this.prototype,t)??{get(){return this[e]},set(r){this[e]=r}};return{get:i,set(r){let h=i?.call(this);n?.call(this,r),this.requestUpdate(t,h,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??at}static _$Ei(){if(this.hasOwnProperty(S("elementProperties")))return;let t=At(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(S("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(S("properties"))){let e=this.properties,s=[...xt(e),...wt(e)];for(let i of s)this.createProperty(i,e[i])}let t=this[Symbol.metadata];if(t!==null){let e=litPropertyMetadata.get(t);if(e!==void 0)for(let[s,i]of e)this.elementProperties.set(s,i)}this._$Eh=new Map;for(let[e,s]of this.elementProperties){let i=this._$Eu(e,s);i!==void 0&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let e=[];if(Array.isArray(t)){let s=new Set(t.flat(1/0).reverse());for(let i of s)e.unshift(L(i))}else t!==void 0&&e.push(L(t));return e}static _$Eu(t,e){let s=e.attribute;return s===!1?void 0:typeof s=="string"?s:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,e=this.constructor.elementProperties;for(let s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return st(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){let s=this.constructor.elementProperties.get(t),i=this.constructor._$Eu(t,s);if(i!==void 0&&s.reflect===!0){let n=(s.converter?.toAttribute!==void 0?s.converter:z).toAttribute(e,s.type);this._$Em=t,n==null?this.removeAttribute(i):this.setAttribute(i,n),this._$Em=null}}_$AK(t,e){let s=this.constructor,i=s._$Eh.get(t);if(i!==void 0&&this._$Em!==i){let n=s.getPropertyOptions(i),r=typeof n.converter=="function"?{fromAttribute:n.converter}:n.converter?.fromAttribute!==void 0?n.converter:z;this._$Em=i;let h=r.fromAttribute(e,n.type);this[i]=h??this._$Ej?.get(i)??h,this._$Em=null}}requestUpdate(t,e,s,i=!1,n){if(t!==void 0){let r=this.constructor;if(i===!1&&(n=this[t]),s??=r.getPropertyOptions(t),!((s.hasChanged??nt)(n,e)||s.useDefault&&s.reflect&&n===this._$Ej?.get(t)&&!this.hasAttribute(r._$Eu(t,s))))return;this.C(t,e,s)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:i,wrapped:n},r){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,r??e??this[t]),n!==!0||r!==void 0)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),i===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,n]of this._$Ep)this[i]=n;this._$Ep=void 0}let s=this.constructor.elementProperties;if(s.size>0)for(let[i,n]of s){let{wrapped:r}=n,h=this[i];r!==!0||this._$AL.has(i)||h===void 0||this.C(i,void 0,n,h)}}let t=!1,e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(s=>s.hostUpdate?.()),this.update(e)):this._$EM()}catch(s){throw t=!1,this._$EM(),s}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(t){}firstUpdated(t){}};m.elementStyles=[],m.shadowRootOptions={mode:"open"},m[S("elementProperties")]=new Map,m[S("finalized")]=new Map,St?.({ReactiveElement:m}),(U.reactiveElementVersions??=[]).push("2.1.2");var K=globalThis,rt=a=>a,D=K.trustedTypes,ot=D?D.createPolicy("lit-html",{createHTML:a=>a}):void 0,ut="$lit$",$=`lit$${Math.random().toFixed(9).slice(2)}$`,_t="?"+$,kt=`<${_t}>`,b=document,C=()=>b.createComment(""),N=a=>a===null||typeof a!="object"&&typeof a!="function",J=Array.isArray,Ct=a=>J(a)||typeof a?.[Symbol.iterator]=="function",B=`[ 	
\f\r]`,k=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,lt=/-->/g,dt=/>/g,f=RegExp(`>|${B}(?:([^\\s"'>=/]+)(${B}*=${B}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),ct=/'/g,ht=/"/g,mt=/^(?:script|style|textarea|title)$/i,G=a=>(t,...e)=>({_$litType$:a,strings:t,values:e}),o=G(1),Bt=G(2),Ft=G(3),x=Symbol.for("lit-noChange"),l=Symbol.for("lit-nothing"),pt=new WeakMap,y=b.createTreeWalker(b,129);function gt(a,t){if(!J(a)||!a.hasOwnProperty("raw"))throw Error("invalid template strings array");return ot!==void 0?ot.createHTML(t):t}var Nt=(a,t)=>{let e=a.length-1,s=[],i,n=t===2?"<svg>":t===3?"<math>":"",r=k;for(let h=0;h<e;h++){let d=a[h],p,u,c=-1,_=0;for(;_<d.length&&(r.lastIndex=_,u=r.exec(d),u!==null);)_=r.lastIndex,r===k?u[1]==="!--"?r=lt:u[1]!==void 0?r=dt:u[2]!==void 0?(mt.test(u[2])&&(i=RegExp("</"+u[2],"g")),r=f):u[3]!==void 0&&(r=f):r===f?u[0]===">"?(r=i??k,c=-1):u[1]===void 0?c=-2:(c=r.lastIndex-u[2].length,p=u[1],r=u[3]===void 0?f:u[3]==='"'?ht:ct):r===ht||r===ct?r=f:r===lt||r===dt?r=k:(r=f,i=void 0);let g=r===f&&a[h+1].startsWith("/>")?" ":"";n+=r===k?d+kt:c>=0?(s.push(p),d.slice(0,c)+ut+d.slice(c)+$+g):d+$+(c===-2?h:g)}return[gt(a,n+(a[e]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),s]},P=class a{constructor({strings:t,_$litType$:e},s){let i;this.parts=[];let n=0,r=0,h=t.length-1,d=this.parts,[p,u]=Nt(t,e);if(this.el=a.createElement(p,s),y.currentNode=this.el.content,e===2||e===3){let c=this.el.content.firstChild;c.replaceWith(...c.childNodes)}for(;(i=y.nextNode())!==null&&d.length<h;){if(i.nodeType===1){if(i.hasAttributes())for(let c of i.getAttributeNames())if(c.endsWith(ut)){let _=u[r++],g=i.getAttribute(c).split($),R=/([.?@])?(.*)/.exec(_);d.push({type:1,index:n,name:R[2],strings:g,ctor:R[1]==="."?I:R[1]==="?"?W:R[1]==="@"?V:A}),i.removeAttribute(c)}else c.startsWith($)&&(d.push({type:6,index:n}),i.removeAttribute(c));if(mt.test(i.tagName)){let c=i.textContent.split($),_=c.length-1;if(_>0){i.textContent=D?D.emptyScript:"";for(let g=0;g<_;g++)i.append(c[g],C()),y.nextNode(),d.push({type:2,index:++n});i.append(c[_],C())}}}else if(i.nodeType===8)if(i.data===_t)d.push({type:2,index:n});else{let c=-1;for(;(c=i.data.indexOf($,c+1))!==-1;)d.push({type:7,index:n}),c+=$.length-1}n++}}static createElement(t,e){let s=b.createElement("template");return s.innerHTML=t,s}};function w(a,t,e=a,s){if(t===x)return t;let i=s!==void 0?e._$Co?.[s]:e._$Cl,n=N(t)?void 0:t._$litDirective$;return i?.constructor!==n&&(i?._$AO?.(!1),n===void 0?i=void 0:(i=new n(a),i._$AT(a,e,s)),s!==void 0?(e._$Co??=[])[s]=i:e._$Cl=i),i!==void 0&&(t=w(a,i._$AS(a,t.values),i,s)),t}var F=class{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:e},parts:s}=this._$AD,i=(t?.creationScope??b).importNode(e,!0);y.currentNode=i;let n=y.nextNode(),r=0,h=0,d=s[0];for(;d!==void 0;){if(r===d.index){let p;d.type===2?p=new O(n,n.nextSibling,this,t):d.type===1?p=new d.ctor(n,d.name,d.strings,this,t):d.type===6&&(p=new q(n,this,t)),this._$AV.push(p),d=s[++h]}r!==d?.index&&(n=y.nextNode(),r++)}return y.currentNode=b,i}p(t){let e=0;for(let s of this._$AV)s!==void 0&&(s.strings!==void 0?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}},O=class a{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,i){this.type=2,this._$AH=l,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,e=this._$AM;return e!==void 0&&t?.nodeType===11&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=w(this,t,e),N(t)?t===l||t==null||t===""?(this._$AH!==l&&this._$AR(),this._$AH=l):t!==this._$AH&&t!==x&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):Ct(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==l&&N(this._$AH)?this._$AA.nextSibling.data=t:this.T(b.createTextNode(t)),this._$AH=t}$(t){let{values:e,_$litType$:s}=t,i=typeof s=="number"?this._$AC(t):(s.el===void 0&&(s.el=P.createElement(gt(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===i)this._$AH.p(e);else{let n=new F(i,this),r=n.u(this.options);n.p(e),this.T(r),this._$AH=n}}_$AC(t){let e=pt.get(t.strings);return e===void 0&&pt.set(t.strings,e=new P(t)),e}k(t){J(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,s,i=0;for(let n of t)i===e.length?e.push(s=new a(this.O(C()),this.O(C()),this,this.options)):s=e[i],s._$AI(n),i++;i<e.length&&(this._$AR(s&&s._$AB.nextSibling,i),e.length=i)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){let s=rt(t).nextSibling;rt(t).remove(),t=s}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},A=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,i,n){this.type=1,this._$AH=l,this._$AN=void 0,this.element=t,this.name=e,this._$AM=i,this.options=n,s.length>2||s[0]!==""||s[1]!==""?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=l}_$AI(t,e=this,s,i){let n=this.strings,r=!1;if(n===void 0)t=w(this,t,e,0),r=!N(t)||t!==this._$AH&&t!==x,r&&(this._$AH=t);else{let h=t,d,p;for(t=n[0],d=0;d<n.length-1;d++)p=w(this,h[s+d],e,d),p===x&&(p=this._$AH[d]),r||=!N(p)||p!==this._$AH[d],p===l?t=l:t!==l&&(t+=(p??"")+n[d+1]),this._$AH[d]=p}r&&!i&&this.j(t)}j(t){t===l?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},I=class extends A{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===l?void 0:t}},W=class extends A{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==l)}},V=class extends A{constructor(t,e,s,i,n){super(t,e,s,i,n),this.type=5}_$AI(t,e=this){if((t=w(this,t,e,0)??l)===x)return;let s=this._$AH,i=t===l&&s!==l||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,n=t!==l&&(s===l||i);i&&this.element.removeEventListener(this.name,this,s),n&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},q=class{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){w(this,t)}};var Pt=K.litHtmlPolyfillSupport;Pt?.(P,O),(K.litHtmlVersions??=[]).push("3.3.3");var $t=(a,t,e)=>{let s=e?.renderBefore??t,i=s._$litPart$;if(i===void 0){let n=e?.renderBefore??null;s._$litPart$=i=new O(t.insertBefore(C(),n),n,void 0,e??{})}return i._$AI(a),i};var Y=globalThis,v=class extends m{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=$t(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return x}};v._$litElement$=!0,v.finalized=!0,Y.litElementHydrateSupport?.({LitElement:v});var Ot=Y.litElementPolyfillSupport;Ot?.({LitElement:v});(Y.litElementVersions??=[]).push("4.2.2");var Z=[["labels","Labels"],["areas","Areas"],["floors","Floors"],["domains","Domains"],["devices","Devices"],["entities","Entities"],["groups","Groups"]],Rt=["device_classes"],Tt=26,jt=[["rules","Rules"],["status","Status"],["explain","Explain"],["settings","Settings"]],Q=()=>Object.fromEntries([...Z.map(([a])=>a),...Rt].map(a=>[a,[]])),Ut=()=>({name:"",enabled:!0,include:Q(),exclude:Q(),actions:[{type:"expose",config:{assistants:["conversation"]}}]}),vt=a=>!Object.values(a||{}).some(t=>t&&t.length);async function Dt(){try{if(customElements.get("ha-selector")&&customElements.get("ha-form"))return;await(await(await window.loadCardHelpers?.())?.createCardElement({type:"entities",entities:[]}))?.constructor?.getConfigElement?.()}catch{}}var X=class extends v{static properties={hass:{attribute:!1},narrow:{type:Boolean},panel:{attribute:!1},_tab:{state:!0},_data:{state:!0},_error:{state:!0},_busy:{state:!0},_editing:{state:!0},_preview:{state:!0},_applyResult:{state:!0},_explain:{state:!0},_explainEntity:{state:!0},_settingsDraft:{state:!0},_showAll:{state:!0}};constructor(){super(),this._tab="rules",this._data=null,this._error="",this._busy=!1,this._editing=null,this._preview=null,this._applyResult=null,this._explain=null,this._explainEntity="",this._settingsDraft=null,this._showAll=!1,this._previewTimer=null}async connectedCallback(){super.connectedCallback(),await Dt(),await Promise.all([this._load(),this._loadNames()])}_ws(t){return this.hass.callWS(t)}async _load(){try{this._data=await this._ws({type:"propsense/overview"}),this._settingsDraft={...this._data.settings},this._error=""}catch(t){this._error=t.message||String(t)}}async _run(t){this._busy=!0;try{await t(),this._error=""}catch(e){this._error=e.message||String(e)}finally{this._busy=!1}}async _loadNames(){this._names={labels:{},areas:{},floors:{}};let t=[["labels","config/label_registry/list","label_id"],["areas","config/area_registry/list","area_id"],["floors","config/floor_registry/list","floor_id"]];await Promise.all(t.map(async([e,s,i])=>{try{for(let n of await this._ws({type:s}))this._names[e][n[i]]=n.name}catch{}})),this.requestUpdate()}_labelName(t){return this._names?.labels?.[t]??this.hass.labels?.[t]?.name??t}_areaName(t){return this._names?.areas?.[t]??this.hass.areas?.[t]?.name??t}_floorName(t){return this._names?.floors?.[t]??this.hass.floors?.[t]?.name??t}_deviceName(t){let e=this.hass.devices?.[t];return e?.name_by_user||e?.name||t}_entityName(t){return this.hass.states?.[t]?.attributes?.friendly_name||t}_valueName(t,e){switch(t){case"labels":return this._labelName(e);case"areas":return this._areaName(e);case"floors":return this._floorName(e);case"devices":return this._deviceName(e);case"entities":case"groups":return this._entityName(e);default:return e}}_targetName(t,e){let s=this._data?.assistants?.find(i=>i.value===e);return t==="expose"&&s?s.label:e}_typeName(t){return this._data?.actions?.find(e=>e.type===t)?.name||t}_summarise(t){let e=Z.filter(([s])=>t?.[s]?.length).map(([s,i])=>`${i}: ${t[s].map(n=>this._valueName(s,n)).join(", ")}`);return e.length?e.join(" \xB7 "):""}_countFor(t){let e=this._data?.last?.rules?.[t.name];return e===void 0?"\u2013":e}async _toggle(t){await this._run(async()=>{await this._ws({type:"propsense/rule/save",rule:{...t,enabled:!t.enabled}}),await this._applyAfterChange()})}async _delete(t){confirm(`Delete the rule "${t.name}"?`)&&await this._run(async()=>{await this._ws({type:"propsense/rule/delete",rule_id:t.id}),await this._applyAfterChange()})}async _applyAfterChange(){await this._ws({type:"propsense/apply",dry_run:!1}),await this._load()}_edit(t){this._editing=JSON.parse(JSON.stringify(t||Ut()));for(let e of["include","exclude"])this._editing[e]={...Q(),...this._editing[e]};this._preview=null,this._showAll=!1,this._schedulePreview()}_setEditing(t){this._editing={...this._editing,...t},this._schedulePreview()}_setSelector(t,e,s){this._setEditing({[t]:{...this._editing[t],[e]:s||[]}})}_schedulePreview(){clearTimeout(this._previewTimer),this._previewTimer=setTimeout(()=>this._runPreview(),400)}async _runPreview(){if(!this._editing)return;let t=this._cleanRule();t.name||(t.name="(draft)");try{this._preview=await this._ws({type:"propsense/preview",rule:t})}catch(e){this._preview={error:e.message||String(e)}}}_cleanRule(){let{id:t,name:e,enabled:s,include:i,exclude:n,actions:r}=this._editing;return{...t?{id:t}:{},name:(e||"").trim(),enabled:s,include:i,exclude:n,actions:r}}async _save(){let t=this._cleanRule();if(!t.name){this._error="Give the rule a name.";return}await this._run(async()=>{await this._ws({type:"propsense/rule/save",rule:t}),this._editing=null,await this._applyAfterChange()})}_addAction(){let t=this._data.actions.find(s=>s.available)?.type||this._data.actions[0].type,e=this._defaultConfig(t);this._setEditing({actions:[...this._editing.actions,{type:t,config:e}]})}_defaultConfig(t){let e=this._data.actions.find(s=>s.type===t)?.schema||[];return Object.fromEntries(e.filter(s=>s.default!==void 0).map(s=>[s.name,s.default]))}_setAction(t,e){let s=this._editing.actions.map((i,n)=>t===n?{...i,...e}:i);this._setEditing({actions:s})}_removeAction(t){this._setEditing({actions:this._editing.actions.filter((e,s)=>s!==t)})}render(){return!this._data&&!this._error?o`<div class="loading">Loading…</div>`:o`
      <div class="toolbar">
        ${this.narrow?o`<ha-menu-button .hass=${this.hass} .narrow=${this.narrow}></ha-menu-button>`:l}
        <div class="title">PropSense</div>
      </div>
      <div class="tabs">
        ${jt.map(([t,e])=>o`<button
            class="tab ${this._tab===t?"active":""}"
            @click=${()=>this._tab=t}
          >${e}</button>`)}
      </div>
      <div class="content">
        ${this._error?o`<div class="error">${this._error}</div>`:l}
        ${this._data?this._renderTab():l}
      </div>
    `}_renderTab(){if(this._editing&&this._tab==="rules")return this._renderEditor();switch(this._tab){case"status":return this._renderStatus();case"explain":return this._renderExplain();case"settings":return this._renderSettings();default:return this._renderRules()}}_renderRules(){let{rules:t,settings:e}=this._data;return o`
      ${!t.length&&!e.dry_run?o`<div class="notice warn">
            <b>Start with a dry run.</b> Rules are the single source of truth: with no rules,
            everything an assistant PropSense manages can see is un-exposed on the next apply.
            <button @click=${()=>this._setDryRun(!0)}>Turn on dry run</button>
          </div>`:l}
      ${e.dry_run?o`<div class="notice">
            Dry run is on: rules are evaluated but nothing is applied.
            <button @click=${()=>this._setDryRun(!1)}>Turn off</button>
          </div>`:l}
      <div class="row">
        <h2>Rules</h2>
        <button class="primary" @click=${()=>this._edit(null)}>Add rule</button>
      </div>
      ${t.length?t.map(s=>this._renderRuleCard(s)):o`<p class="muted">No rules yet. A rule selects entities, for example everything labelled
            “Expose: Novak”, and applies actions such as exposing them to Assist.</p>`}
    `}async _setDryRun(t){await this._run(async()=>{await this._ws({type:"propsense/settings/update",settings:{dry_run:t}}),await new Promise(e=>setTimeout(e,1500)),await this._load()})}_renderRuleCard(t){let e=this._summarise(t.include),s=this._summarise(t.exclude),i=this._data.last?.dormant?.[t.name];return o`<ha-card class="rule ${t.enabled?"":"off"}">
      <div class="rule-head">
        <div>
          <div class="rule-name">${t.name}</div>
          <div class="muted">
            ${t.actions.map(n=>this._typeName(n.type)).join(", ")||"No actions"}
            · ${this._countFor(t)} entities
          </div>
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
      ${s?o`<div class="sel muted">Except: ${s}</div>`:l}
      ${i?o`<div class="warn-text">Dormant action: ${i.join(", ")}. Needs a provider and “Allow third-party actions”.</div>`:l}
    </ha-card>`}_selectorFor(t){switch(t){case"labels":return{label:{multiple:!0}};case"areas":return{area:{multiple:!0}};case"floors":return{floor:{multiple:!0}};case"devices":return{device:{multiple:!0}};case"entities":case"groups":return{entity:{multiple:!0}};default:return{select:{multiple:!0,custom_value:!0,options:[...new Set(Object.keys(this.hass.states).map(s=>s.split(".")[0]))].sort()}}}}_renderSelectorFields(t){let e=this._editing[t];return Z.map(([s,i])=>o`<div class="field">
        <div class="label">${i}</div>
        <ha-selector
          .hass=${this.hass}
          .selector=${this._selectorFor(s)}
          .value=${e[s]||[]}
          @value-changed=${n=>this._setSelector(t,s,n.detail.value)}
        ></ha-selector>
      </div>`)}_renderEditor(){let t=this._editing;return o`
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
                placeholder="For example: Novak voice"
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
            <h3>Include</h3>
            <p class="muted">Every field you fill in must match (and); within a field any value will do (or).</p>
            ${this._renderSelectorFields("include")}
          </ha-card>

          <ha-card class="pad">
            <details ?open=${!vt(t.exclude)}>
              <summary>Exclude (optional)</summary>
              <p class="muted">Entities matching all the fields you fill in here are removed from this rule.</p>
              ${this._renderSelectorFields("exclude")}
            </details>
          </ha-card>

          <ha-card class="pad">
            <div class="row"><h3>Actions</h3>
              <button @click=${this._addAction}>Add action</button></div>
            ${t.actions.length?t.actions.map((e,s)=>this._renderAction(e,s)):o`<p class="warn-text">No actions: this rule does nothing.</p>`}
          </ha-card>
        </div>
        <div class="col">${this._renderPreview()}</div>
      </div>
    `}_renderAction(t,e){let s=this._data.actions,i=s.find(r=>r.type===t.type),n=r=>this._labels[r.name]??r.name.replaceAll("_"," ");return o`<div class="action">
      <div class="row">
        <select @change=${r=>this._setAction(e,{type:r.target.value,config:this._defaultConfig(r.target.value)})}>
          ${s.map(r=>o`<option value=${r.type} ?selected=${r.type===t.type} ?disabled=${!r.available&&r.type!==t.type}>
              ${r.name}${r.available?"":" (enable third-party actions)"}
            </option>`)}
          ${i?l:o`<option selected>${t.type} (not installed)</option>`}
        </select>
        <button class="danger" @click=${()=>this._removeAction(e)}>Remove</button>
      </div>
      ${i?o`${i.available?l:o`<div class="warn-text">Dormant until third-party actions are allowed in Settings.</div>`}
          <ha-form
            .hass=${this.hass}
            .schema=${i.schema}
            .data=${t.config}
            .computeLabel=${n}
            @value-changed=${r=>this._setAction(e,{config:r.detail.value})}
          ></ha-form>`:o`<div class="warn-text">This action type is not installed, so the rule is dormant.</div>`}
    </div>`}_labels={assistants:"Expose to"};_renderPreview(){let t=this._preview,e=this._editing;return o`<ha-card class="pad sticky">
      <h3>Live preview</h3>
      ${vt(e.include)?o`<p class="warn-text">Selects nothing: fill in at least one include field.</p>`:l}
      ${t?t.error?o`<p class="warn-text">${t.error}</p>`:this._renderPreviewBody(t):o`<p class="muted">Working…</p>`}
    </ha-card>`}_renderPreviewBody(t){let e=t.draft,s=e?.entities||[],i=this._showAll?s:s.slice(0,25),n=this._editing.actions.some(r=>r.type==="expose");return o`
      <div class="big">${e?.count??0} <span class="muted">entities selected</span></div>
      ${n?o`<div class="muted">About ${(e?.count??0)*Tt} prompt tokens if exposed to an LLM agent.</div>`:l}
      ${Object.entries(t.assistants||{}).map(([r,h])=>h.refused?o`<div class="warn-text">${this._targetName("expose",r)}: over the size limit, nothing would change.</div>`:l)}
      ${t.blocked&&Object.keys(t.blocked).length?o`<div class="warn-text">Never applied (blocked domain): ${Object.keys(t.blocked).join(", ")}</div>`:l}
      <ul class="entities">
        ${i.map(r=>o`<li><span>${r.name}</span> <span class="muted">${r.entity_id}</span></li>`)}
      </ul>
      ${s.length>i.length?o`<button @click=${()=>this._showAll=!0}>Show all ${s.length}</button>`:l}
    `}_renderStatus(){let t=this._data.last,e=this._applyResult||t;return o`
      <div class="row">
        <h2>Status</h2>
        <div>
          <button ?disabled=${this._busy} @click=${()=>this._apply(!0)}>Dry run</button>
          <button class="primary" ?disabled=${this._busy} @click=${()=>this._apply(!1)}>Apply now</button>
        </div>
      </div>
      ${this._data.settings.dry_run?o`<div class="notice">Dry run is on: “Apply now” changes nothing.</div>`:l}
      ${e?o`
            <p class="muted">${e.dry_run?"Dry run":"Last applied"} ${new Date(e.at).toLocaleString()}</p>
            ${this._renderTargets("expose",e.assistants)}
            ${Object.entries(e.actions||{}).map(([s,i])=>this._renderTargets(s,i))}
            ${Object.keys(e.dormant||{}).length?o`<div class="notice warn">Dormant rules: ${Object.entries(e.dormant).map(([s,i])=>`${s} (${i.join(", ")})`).join("; ")}</div>`:l}
            ${Object.keys(e.blocked||{}).length?o`<div class="notice">Blocked (matched a rule but never applied): ${Object.keys(e.blocked).join(", ")}</div>`:l}
          `:o`<p class="muted">Nothing has been applied yet.</p>`}
    `}_renderTargets(t,e){return Object.entries(e||{}).map(([s,i])=>o`<ha-card class="pad">
        <div class="row">
          <div><b>${this._typeName(t)}</b> → ${this._targetName(t,s)}</div>
          <div>${i.count} entities${t==="expose"?o` · ~${i.estimated_tokens} tokens`:l}</div>
        </div>
        ${i.refused?o`<div class="warn-text">Refused: over the size limit. Nothing was changed.</div>`:l}
        ${i.error?o`<div class="warn-text">Error: ${i.error}</div>`:l}
        ${i.added?.length?o`<div>Adds ${i.added.length}: <span class="muted">${i.added.join(", ")}</span></div>`:l}
        ${i.removed?.length?o`<div>Removes ${i.removed.length}: <span class="muted">${i.removed.join(", ")}</span></div>`:l}
      </ha-card>`)}async _apply(t){await this._run(async()=>{let e=await this._ws({type:"propsense/apply",dry_run:t});this._applyResult=t?e:null,await this._load()})}_renderExplain(){let t=this._explain;return o`
      <h2>Explain an entity</h2>
      <p class="muted">Pick an entity to see which rules select it, and why not.</p>
      <ha-selector
        .hass=${this.hass}
        .selector=${{entity:{}}}
        .value=${this._explainEntity}
        @value-changed=${e=>this._doExplain(e.detail.value)}
      ></ha-selector>
      ${t&&!t.found?o`<p class="warn-text">PropSense doesn't know this entity (it may be disabled).</p>`:l}
      ${t?.found?o`
        <ha-card class="pad">
          <div><b>Labels</b>: ${t.labels.map(e=>this._labelName(e)).join(", ")||"none"}</div>
          <div><b>Area</b>: ${t.area_id?this._areaName(t.area_id):"none"}
            · <b>Floor</b>: ${t.floor_id?this._floorName(t.floor_id):"none"}</div>
          <div><b>Groups</b>: ${t.groups.map(e=>this._entityName(e)).join(", ")||"none"}</div>
        </ha-card>
        ${t.rules.length?t.rules.map(e=>o`<ha-card class="pad">
          <div class="row"><b>${e.name}</b>
            <span class="muted">${e.enabled?e.included?e.excluded?"matches, but excluded":"included":"not included":"disabled"}</span></div>
          ${e.actions.map(s=>o`<div>${this._typeName(s.type)}
            ${s.targets.length?o`→ ${s.targets.map(i=>this._targetName(s.type,i)).join(", ")}`:l}:
            <b class=${s.status==="applies"?"ok":"muted"}>${s.status}</b></div>`)}
        </ha-card>`):o`<p class="muted">No rules.</p>`}`:l}
    `}async _doExplain(t){if(this._explainEntity=t,!t){this._explain=null;return}await this._run(async()=>{this._explain=await this._ws({type:"propsense/explain",entity_id:t})})}_setSetting(t,e){this._settingsDraft={...this._settingsDraft,[t]:e}}_renderSettings(){let t=this._settingsDraft,e=[...new Set(Object.keys(this.hass.states).map(i=>i.split(".")[0]))].sort(),s=(i,n,r)=>o`<label class="check">
      <input type="checkbox" .checked=${!!t[i]} @change=${h=>this._setSetting(i,h.target.checked)} />
      <span>${n}${r?o`<div class="muted">${r}</div>`:l}</span>
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
              @change=${n=>this._setSetting("managed_assistants",n.target.checked?[...new Set([...t.managed_assistants,i.value])]:t.managed_assistants.filter(r=>r!==i.value))} />
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
  `};customElements.define("propsense-panel",X);
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
