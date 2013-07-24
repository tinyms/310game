YUI.add("gallery-datatable-formatters",function(e,t){e.DataTable.Formatters={formatStrings:{general:{type:"number",formatConfig:{decimalPlaces:0}},general2:{type:"number",formatConfig:{decimalPlaces:2}},currency:{type:"number",formatConfig:{prefix:"$",decimalPlaces:0,thousandsSeparator:","}},currency2:{type:"number",formatConfig:{prefix:"$",decimalPlaces:2,thousandsSeparator:","}},currency3:{type:"number",formatConfig:{prefix:"$",decimalPlaces:3,thousandsSeparator:","}},comma:{type:"number",formatConfig:{decimalPlaces:0,thousandsSeparator:","}},comma2:{type:"number",formatConfig:{decimalPlaces:2,thousandsSeparator:","}},comma3:{type:"number",formatConfig:{decimalPlaces:3,thousandsSeparator:","}},shortDate:{type:"date",formatConfig:{format:"%D"}},longDate:{type:"date",formatConfig:{format:"%m/%d/%Y"}},fullDate:{type:"date",formatConfig:{format:"%B %e, %Y"}},isoDate:{type:"date",formatConfig:{format:"%F"}},isoDateTime:{type:"date",formatConfig:{format:"%FT%T"}},array:{type:"array",formatConfig:{value:"value",text:"text"}},object:{type:"object",formatConfig:null},hash:{type:"hash",formatConfig:null},"default":{}},namedFormatter:function(t,n){var r=e.DataTable.Formatters.formatStrings[t]||null,i=n.column.formatOptions||n.column.formatConfig,s=n.value,o,u,a,f,l,c;o=n.column.type||(r?r.type:null),o||(o=i&&i.type?i.type:null),u=n.column.formatConfig||(r?r.formatConfig:null);if(o)switch(o){case"date":s=e.DataType.Date.format(n.value,u);break;case"number":s=e.DataType.Number.format(n.value,u);break;case"array":a=u?u.value:"value",f=u?u.text:"text",e.Array.each(i,function(e){e[a]===n.value&&(s=e[f])});break;case"object":case"hash":l=e.Lang.isString(n.value),e.Object.each(i,function(e,t){c=l?t:+t,c===n.value&&(s=e)})}return s}},e.DataTable.BodyView.prototype._createRowHTML=function(t,n,r){var i=e.Lang,s=i.isArray,o=i.isNumber,u=i.isString,a=i.sub,f=e.Escape.html,l=e.Array,c=e.bind,h=e.Object,p=t.toJSON(),d=t.get("clientId"),v={rowId:this._getRowId(d),clientId:d,rowClass:n%2?this.CLASS_ODD:this.CLASS_EVEN},m=this.host||this,g,y,b,w,E,S;for(g=0,y=r.length;g<y;++g){b=r[g],E=p[b.key],w=b._id||b.key,v[w+"-className"]="",b.formatter&&(S={value:E,data:p,column:b,record:t,className:"",rowClass:"",rowIndex:n},typeof b.formatter=="string"?E!==undefined&&(e.DataTable.Formatters.namedFormatter&&e.DataTable.Formatters.formatStrings[b.formatter]?E=e.DataTable.Formatters.namedFormatter.call(m,b.formatter,S):b.formatConfig?E=a("{"+E+"}",b.formatConfig):E=a(b.formatter,S)):(E=b.formatter.call(m,S),E===undefined&&(E=S.value),v[w+"-className"]=S.className,v.rowClass+=" "+S.rowClass));if(E===undefined||E===null||E==="")E=b.emptyCellValue||"";v[w]=b.allowHTML?E:f(E),v.rowClass=v.rowClass.replace(/\s+/g," ")}return a(this._rowTemplate,v)}},"@VERSION@",{supersedes:[""],requires:["datatype-date-format","datatype-number-format","datatable-base"],optional:[""]});
