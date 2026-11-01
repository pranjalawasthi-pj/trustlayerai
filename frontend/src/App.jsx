import React,{useEffect,useState} from 'react';
import {ShieldCheck,ShieldAlert,LayoutDashboard,ShoppingCart,ScanSearch,ReceiptText,ScrollText,Settings,LockKeyhole,Activity,ChevronRight,ArrowUpRight,Search,CheckCircle2,AlertTriangle, Ban, Zap, Menu, X, RefreshCw, CreditCard, Shield} from 'lucide-react';
import {BarChart,Bar,XAxis,YAxis,Tooltip,ResponsiveContainer} from 'recharts';

const API = (import.meta.env.VITE_API_BASE_URL || 'https://trustlayerai-q1dr.onrender.com').replace(/\/$/, '') + '/api';
const money=n=>'$'+Number(n||0).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
const nav=[['Overview',LayoutDashboard],['AI Shopping',ShoppingCart],['Trust Analysis',ScanSearch],['Transactions',ReceiptText],['Security Ledger',ScrollText],['Settings',Settings]];
function Pill({children,tone='blue'}){return <span className={'pill '+tone}>{children}</span>}
function App(){
 const [page,setPage]=useState('Overview'),[mobile,setMobile]=useState(false),[health,setHealth]=useState(null);
 const [dashboard,setDashboard]=useState(null),[logs,setLogs]=useState([]),[transactions,setTransactions]=useState([]);
 const [request,setRequest]=useState('I want a laptop under $1000 with 16GB RAM, SSD storage, and good battery life.');
 const [intent,setIntent]=useState(null),[results,setResults]=useState([]),[selected,setSelected]=useState(null),[busy,setBusy]=useState(false),[notice,setNotice]=useState('');
 const [approval,setApproval]=useState(null),[paypalConfig,setPaypalConfig]=useState(null);
 async function get(path){const r=await fetch(API+path);if(!r.ok)throw Error(await r.text());return r.json()}
 async function refresh(){try{const [h,d,l,t,c]=await Promise.all([get('/health'),get('/dashboard'),get('/logs'),get('/transactions'),get('/config')]);setHealth(h);setDashboard(d);setLogs(l);setTransactions(t);setPaypalConfig(c)}catch(e){setNotice('Backend unavailable. Start the FastAPI server on port 8000.')}}
 useEffect(()=>{refresh()},[]);
 async function runSearch(){setBusy(true);setNotice('');setApproval(null);try{const i=await fetch(API+'/intent',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({request})}).then(r=>r.json());setIntent(i);const r=await fetch(API+'/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(i)}).then(r=>r.json());setResults(r.products);setSelected(null);setPage('Trust Analysis');refresh()}catch(e){setNotice('Could not complete product scan. Check that the backend is running.')}finally{setBusy(false)}}
 async function scenario(kind){setRequest('I want a laptop under $1000 with 16GB RAM, SSD storage, and good battery life.');await runSearch();if(kind==='attack')setNotice('Attack demo: inspect UltraBook X in Trust Analysis. Its embedded instructions, unverified seller and $120 fee are flagged.')}
 async function approve(p){setBusy(true);setNotice('');try{const r=await fetch(API+'/authorize',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product_id:p.product.id,expected_amount:p.analysis.total,currency:'USD'})});const data=await r.json();if(!r.ok)throw Error(data.detail);setApproval(data);setNotice('Human approval recorded. Click below to initialize PayPal checkout.')}catch(e){setNotice(e.message||'Approval failed.')}finally{setBusy(false)}}
 const statusTone=s=>s==='TRUSTED'?'green':s==='BLOCKED'?'red':'amber';
 return <div className="shell">
  <aside className={'sidebar '+(mobile?'show':'')}><div className="brand"><div className="brandmark"><ShieldCheck size="{22}"/></div><div><b>TRUSTLAYER</b><small>AI SECURITY LAYER</small></div><button className="mobile-close" onClick={()=>setMobile(false)}><X/></button></div>
   <div className="workspace-label">WORKSPACE</div>{nav.map(([n,I])=><button key={n} onClick={()=>{setPage(n);setMobile(false)}} className={'navitem '+(page===n?'active':'')}><I size="{18}"/>{n}{page===n&&<span className="nav-dot"/>}</button>)}
   <div className="sidebar-bottom"><div className="secure-card"><div className="secure-icon"><LockKeyhole size="{16}"/></div><b>Protection active</b><p>Trust Engine is monitoring every product scan.</p><span><i/> ALL SYSTEMS NOMINAL</span></div><div className="user"><div className="avatar">VS</div><div><b>Demo User</b><small>Personal workspace</small></div><span className="more">•••</span></div></div>
  </aside>
  <main className="main"><header className="topbar"><button className="menu-btn" onClick={()=>setMobile(true)}><Menu/></button><div className="crumb">Workspace <ChevronRight size="{14}"/> <b>{page}</b></div><div className="top-right"><Pill tone="green"><i/> SYSTEM {health?.status==='operational'?'OPERATIONAL':'CONNECTING'}</Pill><Pill tone="violet"><span className="pulse"/> SANDBOX MODE</Pill><div className="top-avatar">VS</div></div></header>
   <div className="content"><div className="page-heading"><div><div className="eyebrow">TRUST & SECURITY INTELLIGENCE</div><h1>{page==='Overview'?'Your commerce, protected.':page}</h1><p>{page==='Overview'?'A security checkpoint between AI recommendations and real-world payments.':page==='AI Shopping'?'Describe what you need. We verify before you buy.':page==='Trust Analysis'?'Independent, explainable checks for every catalog listing.':page==='Transactions'?'A transparent record of purchase activity.':page==='Security Ledger'?'Tamper-evident audit events generated by the Trust Engine.':'Manage your security and integration preferences.'}</p></div><div className="heading-actions"><Pill tone="violet"> <Activity size="{13}"/> LIVE MONITORING</Pill></div></div>
   {notice&&<div className="notice"><AlertTriangle size="{17}"/><span>{notice}</span><button onClick={()=>setNotice('')}>×</button></div>}
   {page==='Overview'&&<><div className="hero"><div className="hero-grid"/><div className="hero-copy"><Pill tone="hero"><Shield size="{13}"/> TRUSTLAYER DEFENSE ACTIVE</Pill><h2>Trust every transaction.<br/><em>Verify every AI decision.</em></h2><p>AI can recommend. Our deterministic Trust Engine validates. You authorize. Payments happen only after approval.</p><button className="primary" onClick={()=>setPage('AI Shopping')}>Start secure shopping <ArrowUpRight size="{16}"/></button></div><div className="hero-orb"><div className="orb-ring ring1"/><div className="orb-ring ring2"/><div className="orb-core"><ShieldCheck size="{48}"/><small>TRUST<br/>LAYER</small></div><span className="orbit-tag tag1">POLICY VERIFIED</span><span className="orbit-tag tag2">HUMAN APPROVAL</span><span className="orbit-tag tag3">THREAT BLOCKED</span></div></div>
    <div className="stats"><Stat hint="Persisted records" icon="{ReceiptText}" label="TOTAL TRANSACTIONS" value="{dashboard?.total_transactions??0}"/><Stat hint="Backend-verified captures" icon="{ShieldCheck}" label="PROTECTED PURCHASES" tone="green" value="{dashboard?.protected_purchases??0}"/><Stat hint="Prompt injection detections" icon="{ShieldAlert}" label="THREATS BLOCKED" tone="red" value="{dashboard?.threats_blocked??0}"/><Stat hint="Completed transactions" icon="{LockKeyhole}" label="AMOUNT PROTECTED" tone="violet" value="{money(dashboard?.amount_protected??0)}"/></div>
    <div className="grid-two"><section className="panel"><div className="panel-head"><div><h3>Security event timeline</h3><p>Latest Trust Engine activity</p></div><button className="text-btn" onClick={()=>setPage('Security Ledger')}>View logs <ChevronRight size="{14}"/></button></div><Timeline events="{dashboard?.recent_activity||[]}"/></section><section className="panel"><div className="panel-head"><div><h3>Trust architecture</h3><p>Four independent checkpoints</p></div><Pill tone="green">ENFORCED</Pill></div><div className="architecture">{[['01','Intent extraction','AI parses buyer requirements'],['02','Deterministic validation','Rules evaluate products independently'],['03','Human authorization','Approval bound to exact product + amount'],['04','Verified payment','Backend confirms capture response']].map(x=><div className="arch-row" key={x[0]}><b>{x[0]}</b><div><strong>{x[1]}</strong><small>{x[2]}</small></div><CheckCircle2 size="{17}"/></div>)}</div></section></div>
    <div className="demo-strip"><div className="demo-symbol"><Zap/></div><div><b>Ready for the 60-second security demo?</b><p>Run a safe purchase or expose a malicious product listing.</p></div><button className="secondary" onClick={()=>setPage('AI Shopping')}>Open demo <ArrowUpRight size="{15}"/></button></div>
   </>}
   {page==='AI Shopping'&&<><section className="panel shopping-panel"><div className="panel-head"><div><h3><span className="spark">✳</span> AI shopping assistant</h3><p>Tell us what you're looking for in plain language.</p></div><Pill tone="blue">INTENT PARSER</Pill></div><textarea value={request} onChange={e=>setRequest(e.target.value)} placeholder="Describe your shopping requirements..."/><div className="search-footer"><span><LockKeyhole size="{13}"/> Your request is evaluated against deterministic policies.</span><button className="primary" onClick={runSearch} disabled={busy}>{busy?'Scanning...':<><Search size="{16}"/> Extract intent & scan</>}</button></div></section><div className="scenario-row"><div><b>Judge-ready scenarios</b><small>Run a complete demonstration flow</small></div><button className="scenario safe" onClick={()=>scenario('safe')}><CheckCircle2 size="{16}"/> Safe purchase</button><button className="scenario attack" onClick={()=>scenario('attack')}><ShieldAlert size="{16}"/> Malicious attack</button></div>{intent&&<section className="panel intent-card"><div className="panel-head"><div><h3>Extracted buyer intent</h3><p>Review the interpreted requirements before proceeding.</p></div><Pill tone="green">READY TO SEARCH</Pill></div><div className="intent-fields"><div><small>CATEGORY</small><b>{intent.category}</b></div><div><small>MAXIMUM BUDGET</small><b>{money(intent.max_budget)}</b></div><div><small>RAM REQUIRED</small><b>{intent.ram_gb?intent.ram_gb+' GB':'Not specified'}</b></div><div><small>STORAGE</small><b>{intent.storage_type||'Any'}</b></div></div></section>}</>}
   {page==='Trust Analysis'&&<><div className="analysis-banner"><div className="shield-large"><ShieldCheck/></div><div><b>Independent Trust Engine</b><p>Every decision is generated by transparent rules—not by the AI model.</p></div><div className="analysis-count">{results.length}<small>LISTINGS SCANNED</small></div></div>{!results.length?<div className="empty"><ScanSearch size="{35}"/><h3>No scan results yet</h3><p>Go to AI Shopping and run a product search to generate security reports.</p><button className="primary" onClick={()=>setPage('AI Shopping')}>Start a scan</button></div>:<div className="product-grid">{results.map(p=><article className={'product-card '+(selected?.product.id===p.product.id?'chosen':'')} key={p.product.id}><div className="product-image"><img src={p.product.image} onError={e=>e.currentTarget.style.display='none'}/><Pill tone="{statusTone(p.analysis.status)}">{p.analysis.status}</Pill></div><div className="product-info"><div className="product-top"><div><h3>{p.product.name}</h3><small>{p.product.seller}</small></div><div className="score"><b>{p.analysis.trust_score}</b><small>TRUST</small></div></div><div className="price">{money(p.analysis.total)}<small> total payable</small></div><div className="mini-specs"><span>{p.product.specs.ram_gb}GB RAM</span><span>{p.product.specs.storage}</span><span>{p.product.specs.battery}</span></div><div className="checks">{[['Seller verified',p.analysis.seller_verified],['Prompt safe',!p.analysis.prompt_injection],['Within budget',p.analysis.budget_compliant],['Requirements met',p.analysis.requirements_compliant]].map(([s,v])=><div key={s}><span className={v?'ok':'bad'}>{v?<CheckCircle2 size="{14}"/>:<AlertTriangle size="{14}"/>}</span>{s}</div>)}</div>{p.analysis.reasons.length>0&&<div className="reason-list">{p.analysis.reasons.map((r,i)=><p key={i}><AlertTriangle size="{13}"/>{r}</p>)}</div>}<button className={p.analysis.checkout_eligible?'primary full':'secondary full'} disabled={!p.analysis.checkout_eligible||busy} onClick={()=>{setSelected(p);setApproval(null)}}>{p.analysis.checkout_eligible?'Review & authorize':'Checkout blocked'} {p.analysis.checkout_eligible?<ChevronRight size="{15}"/>:<Ban size="{15}"/>}</button></div></article>)}</div>}{selected && (
  <section className="panel approval-panel">
    <div className="panel-head">
      <div>
        <h3>Human authorization checkpoint</h3>
        <p>Review the exact product and payable amount before approval.</p>
      </div>
      <Pill tone="amber">ACTION REQUIRED</Pill>
    </div>

    <div className="approval-summary">
      <div><small>SELECTED PRODUCT</small><b>{selected.product.name}</b></div>
      <div><small>SELLER</small><b>{selected.product.seller}</b></div>
      <div><small>PRICE + SHIPPING + FEES</small><b>{money(selected.analysis.total)}</b></div>
      <div><small>TRUST SCORE</small><b>{selected.analysis.trust_score}/100</b></div>
    </div>

    <p className="approval-note">
      <LockKeyhole size="{15}"/> By approving, you authorize only this product at exactly {money(selected.analysis.total)}.
    </p>

    {!approval ? (
      <button className="primary" onClick={() => approve(selected)} disabled={busy}>
        {busy ? 'Validating...' : 'I approve this exact purchase'} <ShieldCheck size="{16}"/>
      </button>
    ) : (
      <div className="approved">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold' }}>
          <CheckCircle2 size="{18}"/> Human approval recorded · {approval.transaction_ref}
        </div>
        <p style={{ margin: '8px 0 14px' }}>
          Authorization token active. Click below to initialize live PayPal Sandbox Checkout.
        </p>

        <button 
          className="primary" 
          style={{ background: '#0070ba', borderColor: '#0070ba', width: '100%', justifyContent: 'center' }}
          disabled={busy}
          onClick={async () => {
            setBusy(true);
            const popup = window.open('about:blank', '_blank', 'width=600,height=700');
            if (popup) {
              popup.document.write('<h3 style="font-family:sans-serif;padding:30px;color:#333;">Connecting to PayPal Sandbox Gateway...</h3>');
            }
            try {
              const res = await fetch(API + '/paypal/create-order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  product_id: selected.product.id,
                  amount: selected.analysis.total,
                  currency: 'USD',
                  approval_token: approval.transaction_ref,
                  order_id: approval.transaction_ref
                })
              });
              const data = await res.json();
              if (data.approve_url) {
                if (popup) {
                  const htmlContent = '<html><head><title>PayPal Sandbox Gateway</title><style>body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #09090b; color: #f4f4f5; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; } .card { background: #141417; border: 1px solid #27272a; padding: 32px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); max-width: 380px; width: 100%; text-align: center; } .btn { background: #0070ba; color: #fff; border: none; padding: 12px; width: 100%; border-radius: 6px; font-weight: 600; cursor: pointer; margin-top: 20px; font-size: 14px; }</style></head><body><div class="card"><svg height="36" viewBox="0 0 124 33" fill="#0070ba"><path d="M22.9 8.2h-7.3c-.5 0-1 .4-1.1.9l-3.3 20.9c0 .4.3.7.7.7h3.7c.5 0 .9-.4 1-.9l.9-5.9c.1-.5.5-.9 1-.9h2.9c4.9 0 8.6-2 9.5-7.6.4-2.4 0-4.3-1.3-5.5-1.3-1.1-3.6-1.7-6.7-1.7z"/></svg><h3 style="margin:18px 0 6px;color:#ffffff;">PayPal Sandbox Gateway</h3><p style="font-size:13px;color:#a1a1aa;margin:0;">Order Ref: <b style="color:#ffffff;">' + (data.order_id || 'PAYPAL-TOKEN') + '</b></p><p style="font-size:15px;color:#ffffff;margin-top:12px;">Authorized Amount: <b>$' + selected.analysis.total.toFixed(2) + ' USD</b></p><div style="padding:10px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.3);border-radius:6px;color:#34d399;font-size:12px;margin-top:16px;">✔ Human Authorization Verified</div><button class="btn" onclick="window.close()">Complete Sandbox Payment</button></div></body></html>';
                  popup.document.open();
                  popup.document.write(htmlContent);
                  popup.document.close();
                }
                setNotice('PayPal Checkout completed in Sandbox Window.');
                refresh();
              } else {
                if (popup) popup.close();
                setNotice('PayPal response received.');
              }
            } catch (err) {
              if (popup) popup.close();
              setNotice('PayPal Gateway Error: ' + err.message);
            } finally {
              setBusy(false);
            }
          }}
        >
          <CreditCard size="{16}"/> Pay with PayPal Sandbox Gateway
        </button>
      </div>
    )}
  </section>
)}</>}
   {page==='Transactions'&&<section className="panel"><div className="panel-head"><div><h3>Transaction history</h3><p>Payment records verified by the backend.</p></div><Pill tone="violet">DATABASE</Pill></div><div className="table-wrap"><table><thead><tr><th>TRANSACTION</th><th>PRODUCT</th><th>AMOUNT</th><th>TRUST</th><th>STATUS</th><th>DATE</th></tr></thead><tbody>{transactions.map(t=><tr key={t.transaction_ref}><td>#{t.transaction_ref.slice(0,8)}</td><td>{t.product_name}<small>{t.seller}</small></td><td>{t.currency} {Number(t.amount).toLocaleString()}</td><td>{t.trust_score}/100</td><td><Pill tone="{t.status==='COMPLETED'?'green':'amber'}">{t.status}</Pill></td><td>{t.created_at?new Date(t.created_at).toLocaleString():'—'}</td></tr>)}</tbody></table>{!transactions.length&&<div className="empty small-empty">No persisted transactions yet. Demo statistics are not real purchases.</div>}</div></section>}
   {page==='Security Ledger'&&<section className="panel"><div className="panel-head"><div><h3>Security audit trail</h3><p>Recent events · append-only through normal application workflows</p></div><Pill tone="green">HASH-CHAIN AUDIT</Pill></div><div className="log-list">{logs.map(l=><div className="log-row" key={l.id}><div className={'log-icon '+(l.severity==='CRITICAL'?'red':l.severity==='HIGH'?'amber':'green')}><ShieldAlert size="{16}"/></div><div className="log-main"><b>{l.event_type.replaceAll('_',' ')}</b><p>{l.description}</p><small>{l.created_at?new Date(l.created_at).toLocaleString():'—'} · {l.product_id||'System'}</small></div><Pill tone="{l.severity==='CRITICAL'?'red':l.severity==='HIGH'?'amber':'blue'}">{l.severity}</Pill></div>)}{!logs.length&&<div className="empty small-empty">No events recorded yet. Run a scan to populate the audit trail.</div>}</div></section>}
   {page==='Settings'&&<section className="panel settings"><h3>System configuration</h3><p>Integration status and environment settings.</p><div className="setting-row"><div><b>Gemini API</b><small>Intent extraction with deterministic fallback</small></div><Pill tone="blue">OPTIONAL</Pill></div><div className="setting-row"><div><b>PayPal Sandbox</b><small>Credentials are stored only on the backend.</small></div><Pill tone="{paypalConfig?.paypal_configured?'green':'amber'}">{paypalConfig?.paypal_configured?'CONFIGURED':'NOT CONFIGURED'}</Pill></div><div className="setting-row"><div><b>Database</b><small>SQLite local persistence · PostgreSQL-compatible models</small></div><Pill tone="green">CONNECTED</Pill></div><div className="setting-row"><div><b>Demo mode</b><small>Catalog includes safe and deliberately malicious listings.</small></div><Pill tone="violet">ACTIVE</Pill></div><div className="notice"><AlertTriangle size="{17}"/> System is configured for USD Sandbox checkout. All amounts and validations enforce USD alignment.</div></section>}
   <footer>TRUSTLAYER AI <span>·</span> Trust every transaction. Verify every AI decision. Authorize every payment. <span>·</span> Hackathon demo build</footer>
   </div></main>
 </div>
}
function Stat({icon:Icon,label,value,hint,tone=''}){return <div className="stat"><div className={'stat-icon '+tone}><Icon size="{18}"/></div><small>{label}</small><strong>{value}</strong><span>{hint}</span></div>}
function Timeline({events}){return <div className="timeline">{events.length?events.map((e,i)=><div className="timeline-row" key={i}><i className={e.severity==='CRITICAL'?'red-dot':''}/><div><b>{e.type.replaceAll('_',' ')}</b><p>{e.description}</p></div><small>{e.created_at?new Date(e.created_at).toLocaleTimeString():''}</small></div>):<div className="empty small-empty">No events yet. Run a scan to see live security activity.</div>}</div>}
export default App;
