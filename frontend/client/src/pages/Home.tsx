import { useMemo, useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import {
  Activity, AlertCircle, AlertTriangle, ArrowLeft, ArrowRight, BarChart3, Bell, Bot, Building2,
  CalendarDays, Check, CheckCircle2, ChevronDown, CircleDollarSign, CircleHelp, Clock3, Command, ConciergeBell,
  Cpu, CreditCard, DoorOpen, Download, Gauge, GitBranch, Home as HomeIcon, Hotel, KeyRound, Layers3,
  LifeBuoy, ListFilter, LogOut, Menu, MessageCircle, MoreHorizontal, PackageCheck, PanelLeft, Pause,
  Phone, Play, Plus, Radio, Network, Receipt, RefreshCw, Search, Send, Settings, ShieldAlert, Sparkles,
  Target, Thermometer, TicketCheck, Timer, TrendingUp, UserRound, Users, Wrench, X, Zap
} from "lucide-react";
import { toast } from "sonner";
import { apiClient } from "../lib/api";
import { seedAmenities, seedAssets, seedBookings, seedUsers } from "../data/backendAlignedSeed";
import { AIIntelligenceScreen, DispatchScreen, GuestAmenityDetail, GuestBuggy, GuestCheckout, GuestOffer, GuestFolio, GuestProfile, GuestReservations, GuestSOS, NotificationScreen, ProfileScreen, PropertyHealthScreen, RevenueScreen, SearchOverlay, SentimentScreen, SettingsScreen, StaffNotificationScreen, StaffScheduleScreen, WhatIfScreen, WorkforceScreen } from "./Expansion";

const resortImg = "/manus-storage/resort-villa-clean_eb5956dd.jpg";
void seedAmenities; void seedAssets; void seedBookings; void seedUsers;
type Role = "manager" | "staff" | "guest";
type ManagerPage = "command" | "bookings" | "decisions" | "maintenance" | "amenity" | "forecast" | "revenue" | "workforce" | "sentiment" | "whatif" | "property-health" | "ai-map" | "connected" | "operations" | "emergency" | "notifications" | "profile" | "settings";
type StaffPage = "staff-home" | "tasks" | "schedule" | "dispatch" | "emergency" | "notifications";
type GuestPage = "guest-home" | "concierge" | "amenities" | "amenity-detail" | "waitlist" | "offer" | "buggy" | "folio" | "checkout" | "sos" | "profile";
type Page = ManagerPage | StaffPage | GuestPage;

type DemoState = {
  taskCreated: boolean; taskAccepted: boolean; taskCompleted?: boolean; spaState: "open" | "available" | "maintenance"; offerGuest: "none" | "B" | "C"; guestAsked: boolean; connected: boolean; lastAction: string; highOccupancy?: boolean; guestComplaint?: boolean;
};
const initialDemo: DemoState = { taskCreated:false, taskAccepted:false, taskCompleted:false, spaState:"open", offerGuest:"none", guestAsked:false, connected:false, lastAction:"System ready", highOccupancy:false, guestComplaint:false };

const managerNav = [
  {id:"command", label:"Command Center", icon:Gauge}, {id:"bookings", label:"Bookings", icon:CalendarDays}, {id:"decisions", label:"Intelligence Center", icon:Sparkles}, {id:"maintenance", label:"Maintenance Intelligence", icon:Wrench}, {id:"amenity", label:"Amenity Control", icon:TicketCheck}, {id:"forecast", label:"Occupancy Forecast", icon:TrendingUp}, {id:"revenue", label:"Revenue Intelligence", icon:CircleDollarSign}, {id:"workforce", label:"Workforce Intelligence", icon:Users}, {id:"sentiment", label:"Guest Feedback Intelligence", icon:MessageCircle}, {id:"whatif", label:"What-If Simulator", icon:GitBranch}, {id:"property-health", label:"Property Health", icon:Building2}, {id:"ai-map", label:"System Architecture", icon:Network}, {id:"connected", label:"Connected Intelligence", icon:GitBranch}, {id:"operations", label:"Operations Center", icon:Radio}, {id:"emergency", label:"Emergency Control", icon:ShieldAlert}, {id:"notifications", label:"Notifications", icon:Bell}, {id:"profile", label:"Profile", icon:UserRound}, {id:"settings", label:"Settings", icon:Settings}
] as const;
const staffNav = [
  {id:"staff-home", label:"Staff Home", icon:HomeIcon}, {id:"tasks", label:"My Tasks", icon:ListFilter}, {id:"schedule", label:"Schedule", icon:CalendarDays}, {id:"dispatch", label:"Dispatch", icon:Building2}, {id:"emergency", label:"Emergency", icon:ShieldAlert}, {id:"notifications", label:"Notifications", icon:Bell}
] as const;
const guestNav = [
  {id:"guest-home", label:"My Stay", icon:HomeIcon}, {id:"concierge", label:"AI Concierge", icon:Bot}, {id:"amenities", label:"Amenities", icon:Sparkles}, {id:"waitlist", label:"My Waitlist", icon:Timer}, {id:"offer", label:"Current Offer", icon:TicketCheck}, {id:"buggy", label:"Buggy", icon:ArrowRight}, {id:"folio", label:"Digital Folio", icon:Receipt}, {id:"checkout", label:"Checkout", icon:CheckCircle2}, {id:"sos", label:"Guest SOS", icon:ShieldAlert}, {id:"profile", label:"Profile", icon:UserRound}
] as const;

function Logo({compact=false}:{compact?:boolean}) {
  return <div className="flex items-center gap-3">
    <div className="grid h-9 w-9 place-items-center rounded-lg bg-[#8fd6c2] text-[#132725] shadow-[0_7px_20px_rgba(107,203,173,.16)]"><span className="font-serif text-lg font-bold">S</span></div>
    {!compact && <div className="sr-wordmark-copy"><div className="text-[13px] font-bold tracking-[.02em] text-[#e7eee7]">SMART RESORT <span className="text-[#8fd6c2]">360</span></div><div className="sr-dim mt-0.5 text-[9px] uppercase tracking-[.16em]">Intelligent hospitality</div></div>}
  </div>
}
function Icon({icon: I, size=16}:{icon:any; size?:number}) { return <I size={size} strokeWidth={1.7}/>; }
function StatusChip({children,tone="teal",pulse=false}:{children:React.ReactNode;tone?:"teal"|"amber"|"red"|"blue"|"neutral";pulse?:boolean}) { return <span className={`sr-chip sr-chip-${tone} ${pulse?"sr-live":""}`}><span className="h-1.5 w-1.5 rounded-full bg-current" />{children}</span>; }
function MiniBar({value,color="#7fcbb7"}:{value:number;color?:string}) { return <div className="sr-bar"><span style={{width:`${value}%`,background:color}} /></div>; }
function SectionHeader({eyebrow,title,description,action}:{eyebrow:string;title:string;description?:string;action?:React.ReactNode}) { return <div className="mb-7 flex items-end justify-between gap-4"><div><div className="sr-kicker mb-2">{eyebrow}</div><h1 className="sr-page-title">{title}</h1>{description&&<p className="sr-muted mt-2 max-w-2xl text-sm leading-6">{description}</p>}</div>{action}</div>; }
function Stat({label,value,delta,tone="teal",icon: I}:{label:string;value:string;delta:string;tone?:"teal"|"amber"|"red"|"blue";icon:any}) { const colors={teal:"#8fd6c2",amber:"#e9bc73",red:"#ef9a8e",blue:"#a9c9e9"}; return <div className="sr-surface sr-enter p-5"><div className="flex items-center justify-between"><div className="sr-label">{label}</div><div className="rounded-lg p-2" style={{background:`${colors[tone]}12`,color:colors[tone]}}><Icon icon={I} size={16}/></div></div><div className="sr-number mt-4 text-[28px] font-semibold text-[#f4f0e8]">{value}</div><div className="mt-2 flex items-center gap-2 text-[11px]" style={{color:colors[tone]}}><TrendingUp size={12}/>{delta}</div></div>; }

function Entry({onEnter}:{onEnter:()=>void}) { return <div className="sr-entry">
  <div className="sr-entry-copy"><Logo/><div className="relative z-[1] max-w-xl"><div className="sr-kicker mb-5">PS ID 4 · HACKCELESTIAL 3.0</div><h1 className="font-serif text-[clamp(44px,6vw,82px)] font-medium leading-[.96] tracking-[-.055em] text-[#f2ede2]">From resort data<br/><span className="text-[#8fd6c2]">to intelligent action.</span></h1><p className="sr-muted mt-7 max-w-md text-[15px] leading-7">An intelligent operating layer connecting resort operations, guest experience and revenue intelligence.</p><button className="sr-button mt-9 min-h-12 px-6" onClick={onEnter}>Enter platform <ArrowRight size={16}/></button></div><div className="relative z-[1] flex items-center gap-3 text-[10px] uppercase tracking-[.14em] text-[#718b86]"><span className="h-2 w-2 rounded-full bg-[#8fd6c2]"/> Sense <span>→</span> Predict <span>→</span> Recommend <span>→</span> Act</div></div>
  <div className="sr-entry-art"><img src={resortImg} className="sr-hero-image" alt="Modern resort villa"/><div className="sr-entry-card"><div className="flex items-center justify-between"><StatusChip>Live environment</StatusChip><span className="sr-dim font-mono text-[10px]">v0.9.4</span></div><p className="mt-5 font-serif text-xl leading-tight text-[#f3ede2]">The calm behind every<br/>great guest experience.</p><div className="mt-5 grid grid-cols-3 gap-3 border-t border-white/10 pt-4"><div><div className="sr-label">Occupancy</div><div className="mt-1 text-sm font-semibold">87.4%</div></div><div><div className="sr-label">Guest pulse</div><div className="mt-1 text-sm font-semibold">4.8 <span className="text-[#e9bc73]">★</span></div></div><div><div className="sr-label">Open tasks</div><div className="mt-1 text-sm font-semibold">12</div></div></div></div></div>
</div>; }

function Auth({onLogin}:{onLogin:(role:Role)=>void}) {
  const { loginGuest, requestGuestOTP, loginStaff, loginManager, setRoleOverride } = useAuth();
  const [role, setRole] = useState<Role>("manager");
  const [step, setStep] = useState<1|2>(1);
  const [email, setEmail] = useState("ananya.manager@smartresort360.com");
  const [password, setPassword] = useState("Manager@123");
  const [empId, setEmpId] = useState("ENG001");
  const [pin, setPin] = useState("1234");
  const [guestEmail, setGuestEmail] = useState("aarav@example.com");
  const [otp, setOtp] = useState("1234");
  const [loading, setLoading] = useState(false);

  const handleContinue = async () => {
    setLoading(true);
    try {
      if (role === "guest") {
        await requestGuestOTP(guestEmail);
        toast.success("OTP sent to your booking email");
        setStep(2);
      } else if (role === "staff") {
        await loginStaff(empId, pin);
        toast.success("Staff authenticated via JWT");
        onLogin(role);
      } else {
        await loginManager(email, password);
        toast.success("Manager authenticated via JWT");
        onLogin(role);
      }
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Authentication failed");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async () => {
    setLoading(true);
    try {
      await loginGuest(guestEmail, otp);
      toast.success("Guest verified via OTP");
      onLogin("guest");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Invalid OTP verification");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sr-auth">
      <div className="sr-auth-card sr-enter">
        <div className="flex items-center justify-between">
          <Logo/>
          <button className="sr-button-quiet" onClick={()=>toast("Help center opened")}><CircleHelp size={16}/></button>
        </div>
        <div className="mt-12">
          <div className="sr-kicker mb-3">Secure access · single property</div>
          <h1 className="font-serif text-3xl text-[#f3eee6]">Welcome to Smart Resort 360</h1>
          <p className="sr-muted mt-2 text-sm">Choose your workspace to continue.</p>
        </div>
        <div className="sr-segment mt-7">
          {(["manager","staff","guest"] as Role[]).map(r=>(
            <button key={r} onClick={()=>{
              setRole(r);
              setStep(1);
              if(r==="guest") setGuestEmail("aarav@example.com");
              else if(r==="staff") { setEmpId("ENG001"); setPin("1234"); }
              else { setEmail("ananya.manager@smartresort360.com"); setPassword("StrongPass!1"); }
            }} className={role===r?"active":""}>
              {r[0].toUpperCase()+r.slice(1)}
            </button>
          ))}
        </div>
        {step===1 ? (
          <div className="mt-6">
            {role==="guest"? (
              <>
                <label className="sr-label mb-2 block">Booking Email</label>
                <input className="sr-input" value={guestEmail} onChange={e=>setGuestEmail(e.target.value)}/>
              </>
            ) : role==="staff"? (
              <div className="grid gap-3">
                <div>
                  <label className="sr-label mb-2 block">Employee ID</label>
                  <input className="sr-input" value={empId} onChange={e=>setEmpId(e.target.value)}/>
                </div>
                <div>
                  <label className="sr-label mb-2 block">PIN</label>
                  <input className="sr-input" type="password" value={pin} onChange={e=>setPin(e.target.value)}/>
                </div>
              </div>
            ) : (
              <div className="grid gap-3">
                <div>
                  <label className="sr-label mb-2 block">Email</label>
                  <input className="sr-input" value={email} onChange={e=>setEmail(e.target.value)}/>
                </div>
                <div>
                  <label className="sr-label mb-2 block">Password</label>
                  <input className="sr-input" type="password" value={password} onChange={e=>setPassword(e.target.value)}/>
                </div>
              </div>
            )}
            <button className="sr-button mt-6 w-full min-h-11" disabled={loading} onClick={handleContinue}>
              {loading ? "Authenticating..." : role === "guest" ? "Send OTP" : "Continue"} <ArrowRight size={15}/>
            </button>
          </div>
        ) : (
          <div className="mt-6">
            <div className="flex items-center gap-3">
              <button onClick={()=>setStep(1)} className="sr-button-quiet"><ArrowLeft size={15}/></button>
              <div>
                <div className="text-sm font-semibold">Verify your stay</div>
                <div className="sr-muted mt-1 text-xs">Enter the verification code sent to {guestEmail}</div>
              </div>
            </div>
            <div className="mt-5">
              <input className="sr-input text-center text-xl tracking-widest" maxLength={6} value={otp} onChange={e=>setOtp(e.target.value)}/>
            </div>
            <button className="sr-button mt-6 w-full min-h-11" disabled={loading} onClick={handleVerifyOtp}>
              {loading ? "Verifying..." : "Verify & Enter"} <Check size={15}/>
            </button>
            <button className="sr-button-quiet mt-3 w-full" onClick={()=>requestGuestOTP(guestEmail).then(()=>toast.info("Resent OTP"))}>Resend Code</button>
          </div>
        )}
        <div className="mt-9 flex items-center justify-between border-t border-white/10 pt-5 text-[10px] text-[#6d8781]">
          <span>Privacy & security</span>
          <span>HackHustlers · HackCelestial 3.0</span>
        </div>
      </div>
    </div>
  );
}


function Sidebar({role,page,setPage,onLogout,onDemo}:{role:Role;page:Page;setPage:(p:Page)=>void;onLogout:()=>void;onDemo:()=>void}) { const nav=role==="manager"?managerNav:role==="staff"?staffNav:guestNav; return <aside className="sr-sidebar"><Logo compact={false}/><div className="mt-10 mb-3 flex items-center justify-between"><span className="sr-label">Workspace</span><StatusChip tone={role==="guest"?"amber":"teal"}>{role[0].toUpperCase()+role.slice(1)}</StatusChip></div><nav className="space-y-1">{nav.map(({id,label,icon})=><button key={id} className={`sr-nav-item ${page===id?"active":""}`} onClick={()=>setPage(id as Page)}><Icon icon={icon}/><span className="sr-nav-copy">{label}</span>{id==="decisions"&&<span className="ml-auto sr-nav-copy rounded-full bg-[#d99568] px-1.5 py-0.5 text-[9px] text-[#1c1a17]">4</span>}</button>)}</nav><div className="mt-auto"><button className="sr-nav-item" onClick={onDemo}><Icon icon={Zap}/><span className="sr-nav-copy">Demo mode</span></button><button className="sr-nav-item" onClick={onLogout}><Icon icon={LogOut}/><span className="sr-nav-copy">Log out</span></button><div className="mt-4 rounded-xl border border-white/8 bg-white/[.03] p-3"><div className="flex items-center gap-2"><div className="grid h-7 w-7 place-items-center rounded-full bg-[#47665e] text-[10px] font-bold">{role==="manager"?"AV":role==="staff"?"ST":"GU"}</div><div className="sr-nav-copy"><div className="text-[11px] font-semibold">{role==="manager"?"Ava Stone":role==="staff"?"Engineering Staff":"Authenticated Guest"}</div><div className="sr-dim text-[10px]">{role[0].toUpperCase()+role.slice(1)}</div></div><MoreHorizontal className="ml-auto sr-nav-copy text-[#7e9994]" size={15}/></div></div></div></aside>; }

function Topbar({role,page,setPage,onDemo,onSearch}:{role:Role;page:Page;setPage:(p:Page)=>void;onDemo:()=>void;onSearch:()=>void}) { const title=page.replace("staff-home","Staff home").replace("guest-home","My stay").replace("-"," "); return <header className="sr-topbar"><div className="flex items-center gap-3"><button className="sr-button-quiet sr-mobile-menu"><Menu size={18}/></button><div className="sr-dim text-xs">Sunridge Cove /</div><div className="text-xs font-semibold capitalize text-[#dce7df]">{title}</div></div><div className="flex items-center gap-2"><button className="sr-button-quiet sr-search-trigger hidden sm:inline-flex" onClick={onSearch}><Search size={16}/><span className="hidden md:inline">Search</span><kbd className="sr-chip ml-1 px-1.5 text-[9px]">⌘ K</kbd></button><button className="sr-button-quiet" onClick={()=>setPage("notifications" as Page)}><Bell size={17}/><span className="ml-[-5px] mt-[-12px] grid h-3.5 w-3.5 place-items-center rounded-full bg-[#d99568] text-[8px] text-[#1c1a17]">4</span></button><button className="sr-button-quiet" onClick={onDemo}><Zap size={16}/><span className="hidden md:inline text-[11px]">Demo</span></button><div className="ml-1 grid h-8 w-8 place-items-center rounded-full bg-[#46645d] text-[10px] font-bold">{role==="manager"?"AV":role==="staff"?"ST":"GU"}</div></div></header>; }

function AppShell({role,setRole,page,setPage,onLogout,onDemo,onSearch,children}:{role:Role;setRole:(r:Role)=>void;page:Page;setPage:(p:Page)=>void;onLogout:()=>void;onDemo:()=>void;onSearch:()=>void;children:React.ReactNode}) { return <div className={`sr-app ${role==="guest"?"sr-guest":""}`}><div className="sr-shell"><Sidebar role={role} page={page} setPage={setPage} onLogout={onLogout} onDemo={onDemo}/><div className="sr-main"><Topbar role={role} page={page} setPage={setPage} onDemo={onDemo} onSearch={onSearch}/>{children}</div></div></div>; }

function CommandCenter({demo,setDemo,setPage}:{demo:DemoState;setDemo:React.Dispatch<React.SetStateAction<DemoState>>;setPage:(p:Page)=>void}) { return <main className="sr-content"><SectionHeader eyebrow="Wednesday · 26 September 2026 · 10:42 IST" title="Good morning, Ananya." description="The resort is operating normally. Here's what needs your attention today." action={<button className="sr-button sr-button-secondary" onClick={()=>setPage("decisions")}>Open decision stream <ArrowRight size={14}/></button>}/><div className="sr-grid sr-grid-4"><Stat label="Occupancy" value="87.4%" delta="+6.8% vs last week" icon={Building2}/><Stat label="Revenue pace" value="Pending backend data" delta="+12.4% ahead of plan" tone="blue" icon={TrendingUp}/><Stat label="Guest sentiment" value="4.8 / 5" delta="+0.2 this week" icon={MessageCircle}/><Stat label="Open attention" value="12" delta="3 need action today" tone="amber" icon={AlertTriangle}/></div><div className="mt-7 grid gap-5 lg:grid-cols-[1.25fr_.75fr]"><div className="sr-surface sr-enter sr-delay-1 p-5"><div className="flex items-start justify-between"><div><div className="sr-kicker">Sense / Predict</div><h2 className="mt-2 font-serif text-[23px] text-[#f3eee6]">Occupancy snapshot</h2><p className="sr-muted mt-1 text-xs">Live rooms and 7-day forecast</p></div><StatusChip>Live · updated 2m ago</StatusChip></div><div className="mt-8 flex items-end gap-1" style={{height:150}}>{[58,64,69,73,79,87,84,81,76,82,89,92,90,87,86,88,91,93,94,91,88,86,84,87].map((v,i)=><div key={i} className="group relative flex-1" style={{height:`${v}%`}}><div className={`h-full rounded-t-sm ${i>13?"bg-[#578476]/55":"bg-[#72b9a4]"}`}><div className="absolute bottom-full left-1/2 mb-2 hidden -translate-x-1/2 rounded bg-[#0b1516] px-2 py-1 text-[9px] text-white group-hover:block">{v}%</div></div></div>)}</div><div className="mt-3 flex justify-between text-[10px] text-[#6f8983]"><span>24 Sep</span><span>Today</span><span>30 Sep</span></div><div className="mt-5 grid grid-cols-3 gap-4 border-t border-white/8 pt-4"><div><div className="sr-label">Rooms occupied</div><div className="mt-1 text-sm font-semibold">248 / 284</div></div><div><div className="sr-label">Forecast high</div><div className="mt-1 text-sm font-semibold text-[#8fd6c2]">93% <span className="sr-muted text-[10px]">Fri</span></div></div><div><div className="sr-label">Demand signal</div><div className="mt-1 text-sm font-semibold text-[#e9bc73]">Elevated</div></div></div></div><div className="sr-surface sr-enter sr-delay-2 p-5"><div className="flex items-start justify-between"><div><div className="sr-kicker">Act</div><h2 className="mt-2 font-serif text-[23px] text-[#f3eee6]">Operational attention</h2></div><button className="sr-button-quiet" onClick={()=>setPage("decisions")}>View all <ArrowRight size={14}/></button></div><div className="mt-5 space-y-3"><AttentionRow tone="red" icon={Thermometer} title="SPA_HEATER at high risk" meta="Preventive action due · 84 risk" onClick={()=>setPage("maintenance")}/><AttentionRow tone="amber" icon={Users} title="Spa waitlist has 8 guests" meta="Next slot forecast in 90 min" onClick={()=>setPage("amenity")}/><AttentionRow tone="blue" icon={MessageCircle} title="Sentiment dip detected" meta="Poolside service · 6 mentions" onClick={()=>setPage("decisions")}/></div><div className="mt-5 rounded-lg border border-[#8fd6c2]/15 bg-[#8fd6c2]/[.06] p-3"><div className="flex gap-2"><Sparkles className="mt-0.5 text-[#8fd6c2]" size={15}/><div><div className="text-xs font-semibold text-[#cbeade]">AI has 4 recommendations ready</div><div className="sr-muted mt-1 text-[10px] leading-4">The decision stream has grouped them by urgency and impact.</div></div></div></div></div></div><DecisionStream demo={demo} setPage={setPage} compact setDemo={setDemo}/></main>; }
function AttentionRow({tone,icon,title,meta,onClick}:{tone:"red"|"amber"|"blue";icon:any;title:string;meta:string;onClick:()=>void}) { return <button onClick={onClick} className="flex w-full items-center gap-3 rounded-lg p-2.5 text-left hover:bg-white/[.04]"><div className={`rounded-lg p-2 ${tone==="red"?"bg-[#d95f58]/10 text-[#ef9a8e]":tone==="amber"?"bg-[#dfae52]/10 text-[#e9bc73]":"bg-[#609bd8]/10 text-[#a9c9e9]"}`}><Icon icon={icon} size={15}/></div><div className="min-w-0 flex-1"><div className="truncate text-xs font-semibold text-[#dfe9e2]">{title}</div><div className="sr-muted mt-1 truncate text-[10px]">{meta}</div></div><ArrowRight size={14} className="text-[#68827d]"/></button>; }

function DecisionStream({demo,setPage,compact=false,setDemo}:{demo:DemoState;setPage:(p:Page)=>void;compact?:boolean;setDemo:React.Dispatch<React.SetStateAction<DemoState>>}) { const actions = demo.connected ? [{time:"10:43:02",label:"Spa marked unavailable",detail:"Maintenance event synced to scheduler",tone:"red",icon:Wrench},{time:"10:43:04",label:"Alternatives recalculated",detail:"3 context-aware amenities ranked for Guest Queue Entry",tone:"teal",icon:Sparkles},{time:"10:43:05",label:"Concierge notified",detail:"Guest-facing recommendation is ready",tone:"blue",icon:Bot},{time:"10:43:07",label:"Manager informed",detail:"Decision chain added to your stream",tone:"amber",icon:Bell}] : [{time:"10:42:18",label:"Preventive inspection recommended",detail:"SPA_HEATER · 84 risk · 3 signals",tone:"red",icon:Wrench},{time:"10:40:09",label:"Spa capacity forecast updated",detail:"8 guests waiting · next slot 90 min",tone:"amber",icon:TicketCheck},{time:"10:36:44",label:"Revenue pace above plan",detail:"+12.4% · weekend demand elevated",tone:"teal",icon:TrendingUp},{time:"10:32:07",label:"Sentiment cluster detected",detail:"Poolside service · 6 mentions",tone:"blue",icon:MessageCircle}]; return <div className="sr-surface sr-enter sr-delay-2 mt-5 p-5"><div className="flex items-start justify-between"><div><div className="sr-kicker">Sense → Predict → Recommend → Act</div><h2 className="mt-2 font-serif text-[23px] text-[#f3eee6]">Intelligence Center</h2><p className="sr-muted mt-1 text-xs">A live, explainable record of intelligence becoming action.</p></div><div className="flex items-center gap-2"><StatusChip pulse>Live stream</StatusChip>{compact&&<button className="sr-button-quiet" onClick={()=>setPage("decisions")}>Open full view <ArrowRight size={14}/></button>}</div></div><div className={`mt-5 ${compact?"grid gap-3 md:grid-cols-4":"space-y-2"}`}>{actions.slice(0,compact?4:10).map((a,i)=><div key={a.time} className={`flex items-start gap-3 rounded-lg border border-white/7 bg-white/[.025] p-3 ${i===0?"sr-live":""}`}><div className={`rounded-lg p-2 ${a.tone==="red"?"bg-[#d95f58]/10 text-[#ef9a8e]":a.tone==="amber"?"bg-[#dfae52]/10 text-[#e9bc73]":a.tone==="blue"?"bg-[#609bd8]/10 text-[#a9c9e9]":"bg-[#65b899]/10 text-[#8fd6c2]"}`}><Icon icon={a.icon} size={14}/></div><div className="min-w-0 flex-1"><div className="flex items-center justify-between gap-2"><span className="text-[11px] font-semibold text-[#e0ebe3]">{a.label}</span><span className="sr-dim font-mono text-[9px]">{a.time}</span></div><div className="sr-muted mt-1 text-[10px] leading-4">{a.detail}</div></div></div>)}</div>{!compact&&<div className="mt-4 flex items-center gap-2"><button className="sr-button sr-button-secondary" onClick={()=>{setDemo(d=>({...d,connected:true,lastAction:"Decision stream expanded"}));toast("Connected chain is now live")}}><Play size={14}/> Simulate next decision</button><span className="sr-muted text-[10px]">Demo controls keep this stream deterministic.</span></div>}</div>; }

function Maintenance({demo,setDemo,setPage,setRole}:{demo:DemoState;setDemo:React.Dispatch<React.SetStateAction<DemoState>>;setPage:(p:Page)=>void;setRole:(r:Role)=>void}) {
  const [assets, setAssets] = useState<any[]>([]);
  const [selectedAssetId, setSelectedAssetId] = useState<number | null>(null);
  const [evalResult, setEvalResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAssets();
  }, []);

  const fetchAssets = async () => {
    try {
      const res = await apiClient.get("/maintenance/assets");
      setAssets(res.data);
      if (res.data.length > 0) {
        setSelectedAssetId(res.data[0].asset_id);
      }
    } catch (err) {
      toast.error("Failed to load assets from backend");
    }
  };

  const handleEvaluate = async (assetId: number) => {
    setLoading(true);
    try {
      const res = await apiClient.post(`/maintenance/${assetId}/evaluate`);
      setEvalResult(res.data);
      toast.success(`Evaluated Asset ${assetId}: Risk Score ${res.data.risk_score}`);
    } catch (err) {
      toast.error("Evaluation failed");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTicket = async () => {
    try {
      await apiClient.post("/tickets", {
        location: "Guest Tower · Spa Heater",
        issue_category: "PREVENTIVE_INSPECTION",
        department: "ENGINEERING",
        urgency: "HIGH"
      });
      setDemo(d=>({...d, taskCreated: true, lastAction: "Preventive task created for SPA_HEATER via FastAPI"}));
      toast.success("Preventive inspection ticket created in FastAPI database!");
    } catch (err) {
      toast.error("Failed to create ticket");
    }
  };

  const selectedAsset = assets.find(a => a.asset_id === selectedAssetId) || {
    asset_id: 1,
    asset_type: "HVAC_UNIT",
    room_or_location: "Spa",
    installation_date: "2020-01-01",
    last_service_date: "2025-08-01",
    service_interval_days: 180
  };

  return (
    <main className="sr-content">
      <SectionHeader
        eyebrow="Property health / Predictive maintenance"
        title="Maintenance Intelligence"
        description="Know what will fail before it interrupts a guest stay. (Live FastAPI Risk Model)"
        action={
          <button className="sr-button" onClick={handleCreateTicket}>
            <Plus size={15}/> Create preventive task
          </button>
        }
      />
      <div className="sr-grid sr-grid-4">
        <Stat label="Assets monitored" value={assets.length ? assets.length.toString() : "1"} delta="100% database coverage" icon={Cpu}/>
        <Stat label="At elevated risk" value="1" delta="SPA_HEATER" tone="amber" icon={AlertTriangle}/>
        <Stat label="Avoided downtime" value="31.2h" delta="This quarter" icon={Clock3}/>
        <Stat label="Prediction confidence" value="100%" delta="Transparent Weighted Scoring" tone="blue" icon={Target}/>
      </div>
      <div className="mt-7 grid gap-5 xl:grid-cols-[1.08fr_.92fr]">
        <div className="sr-surface overflow-hidden">
          <div className="flex items-center justify-between p-5">
            <div>
              <div className="sr-kicker">Asset table</div>
              <h2 className="mt-2 font-serif text-[23px]">Risk-ranked assets</h2>
            </div>
            <button className="sr-button-quiet" onClick={fetchAssets}><RefreshCw size={15}/> Refresh</button>
          </div>
          <div className="sr-table-row grid-cols-[1.2fr_.7fr_.9fr_.8fr] border-y border-white/8 bg-white/[.02] text-[10px] uppercase tracking-[.1em] text-[#718a85]">
            <span>Asset</span><span>Location</span><span>Last Service</span><span>Action</span>
          </div>
          {assets.length === 0 ? (
            <div className="p-4 text-xs text-[#718a85]">Loading assets from backend...</div>
          ) : (
            assets.map(a => (
              <button key={a.asset_id} onClick={()=>setSelectedAssetId(a.asset_id)} className={`sr-table-row w-full grid-cols-[1.2fr_.7fr_.9fr_.8fr] text-left ${selectedAssetId===a.asset_id?"bg-[#8fd6c2]/[.06]":""}`}>
                <div>
                  <div className="text-xs font-semibold text-[#dfe9e2]">{a.asset_type} (#{a.asset_id})</div>
                  <div className="sr-muted mt-1 text-[10px]">{a.room_or_location}</div>
                </div>
                <div className="text-xs text-[#dce9e0]">{a.room_or_location}</div>
                <div className="sr-muted text-[10px]">{a.last_service_date}</div>
                <button className="sr-chip sr-chip-teal text-[9px]" onClick={(e)=>{ e.stopPropagation(); handleEvaluate(a.asset_id); }}>
                  Evaluate
                </button>
              </button>
            ))
          )}
        </div>
        <AssetDetail
          asset={{
            id: `ASSET-${selectedAsset.asset_id}`,
            name: `${selectedAsset.room_or_location} · ${selectedAsset.asset_type}`,
            risk: evalResult ? Math.round(evalResult.risk_score * 100) : 84
          }}
          taskCreated={demo.taskCreated}
          taskAccepted={demo.taskAccepted}
          taskCompleted={demo.taskCompleted}
          onCreate={handleCreateTicket}
          onStaff={()=>{setRole("staff");setPage("tasks")}}
        />
      </div>
      <div className="mt-5 sr-surface p-5">
        <div className="sr-kicker">How the prediction was made (Backend Formula)</div>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          <Reason label="Service Overdue (30%)" value={evalResult ? `${(evalResult.risk_score * 0.3 * 100).toFixed(1)} pts` : "+30.0 pts"} detail="Days since last service" tone="red"/>
          <Reason label="Asset Age (20%)" value="+20.0 pts" detail="Years since installation" tone="amber"/>
          <Reason label="Previous Faults (20%)" value="+20.0 pts" detail="Logged maintenance records" tone="blue"/>
        </div>
      </div>
    </main>
  );
}

function Reason({label,value,detail,tone}:{label:string;value:string;detail:string;tone:"red"|"amber"|"blue"}) { return <div className="sr-surface-soft p-4"><div className="flex items-center justify-between"><span className="sr-label">{label}</span><span className={`text-xs font-semibold ${tone==="red"?"text-[#ef9a8e]":tone==="amber"?"text-[#e9bc73]":"text-[#a9c9e9]"}`}>{value}</span></div><div className="sr-muted mt-3 text-[11px] leading-5">{detail}</div></div>; }
function AssetDetail({asset,taskCreated,taskAccepted,taskCompleted,onCreate,onStaff}:{asset:any;taskCreated:boolean;taskAccepted:boolean;taskCompleted?:boolean;onCreate:()=>void;onStaff:()=>void}) { return <div className="sr-surface sr-enter sr-delay-1 p-5"><div className="flex items-start justify-between"><div><div className="sr-kicker">Asset details</div><div className="mt-2 flex items-center gap-3"><h2 className="font-serif text-[25px]">{asset.id}</h2><StatusChip tone="red" pulse>High risk</StatusChip></div><div className="sr-muted mt-1 text-xs">{asset.name}</div></div><button className="sr-button-quiet"><MoreHorizontal size={17}/></button></div><div className="mt-6 rounded-xl border border-[#d95f58]/20 bg-[#d95f58]/[.06] p-4"><div className="flex gap-3"><AlertCircle className="mt-0.5 text-[#ef9a8e]" size={17}/><div><div className="text-sm font-semibold text-[#f4c1b9]">Preventive inspection recommended</div><div className="sr-muted mt-1 text-[11px] leading-5">A service interruption is likely within the next 5–7 days if service remains overdue under high room usage.</div></div></div></div><div className="mt-5 grid grid-cols-2 gap-3"><div className="sr-surface-soft p-3"><div className="sr-label">Risk score</div><div className="sr-number mt-2 text-2xl text-[#ef9a8e]">{asset.risk}<span className="sr-muted text-xs"> / 100</span></div></div><div className="sr-surface-soft p-3"><div className="sr-label">Confidence</div><div className="sr-number mt-2 text-2xl text-[#8fd6c2]">92<span className="sr-muted text-xs">%</span></div></div></div><div className="mt-5"><div className="flex items-center justify-between"><div className="sr-label">Recommended action</div><span className="text-[10px] text-[#8fd6c2]">30 min · low disruption</span></div><div className="mt-3 rounded-lg border border-white/8 bg-white/[.03] p-3"><div className="text-xs font-semibold">Inspect compressor and belt tension</div><div className="sr-muted mt-1 text-[10px]">Route to Engineering · priority P1 · before 14:00 today</div></div></div>{taskCreated?<div className="mt-5 rounded-lg border border-[#8fd6c2]/20 bg-[#8fd6c2]/[.07] p-3"><div className="flex items-center gap-2 text-xs font-semibold text-[#c7efdf]"><CheckCircle2 size={15}/> TICKET-SPA-001 routed to Engineering Department</div><div className="sr-muted mt-1 pl-6 text-[10px]">Engineering · due today · {taskCompleted?"Completed by staff":taskAccepted?"Accepted by staff":"Awaiting acceptance"}</div><button className="sr-button-quiet mt-2 ml-4" onClick={onStaff}>Open staff view <ArrowRight size={13}/></button></div>:<button className="sr-button mt-5 w-full" onClick={onCreate}>Create preventive inspection <ArrowRight size={14}/></button>}</div>; }

function Amenity({demo,setDemo,setPage}:{demo:DemoState;setDemo:React.Dispatch<React.SetStateAction<DemoState>>;setPage:(p:Page)=>void}) {
  const [amenitiesList, setAmenitiesList] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAmenities();
  }, []);

  const fetchAmenities = async () => {
    try {
      const res = await apiClient.get("/amenities");
      setAmenitiesList(res.data);
    } catch (err) {
      toast.error("Failed to load amenities");
    }
  };

  const available = demo.spaState !== "maintenance";
  const offer = demo.offerGuest;

  const handleJoinWaitlist = async (amenityId: number) => {
    try {
      const res = await apiClient.post(`/amenities/${amenityId}/waitlist`, {
        guest_id: "GUEST-001",
        booking_id: 1,
        vip_tier: "SUITE"
      });
      toast.success(`Joined waitlist ID: ${res.data.waitlist_id}`);
      setDemo(d => ({ ...d, lastAction: `Joined waitlist for Amenity ${amenityId}` }));
    } catch (err) {
      toast.error("Waitlist join failed");
    }
  };

  const handleAcceptOffer = async (amenityId: number, offerId: number) => {
    try {
      const res = await apiClient.post(`/amenities/${amenityId}/offers/${offerId}/accept`);
      toast.success(res.data.message);
      setDemo(d => ({ ...d, offerGuest: "none", lastAction: `Accepted offer ${offerId}` }));
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Accept offer failed");
    }
  };

  const handleSkipOffer = async (amenityId: number, offerId: number) => {
    try {
      const res = await apiClient.post(`/amenities/${amenityId}/offers/${offerId}/skip`);
      toast.info(res.data.message);
      setDemo(d => ({ ...d, offerGuest: "C", lastAction: `Skipped offer ${offerId}` }));
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Skip offer failed");
    }
  };

  return (
    <main className="sr-content">
      <SectionHeader
        eyebrow="Guest experience / Dynamic scheduling"
        title="Amenity Control"
        description="Turn changing capacity into fair, explainable guest outcomes. (FastAPI Dynamic Scheduler)"
        action={
          <div className="flex gap-2">
            <button className="sr-button sr-button-secondary" onClick={()=>setDemo(d=>({...d,spaState:"maintenance",connected:true,lastAction:"Luxury Spa maintenance triggered"}))}>
              <Wrench size={14}/> Trigger maintenance
            </button>
            <button className="sr-button" onClick={()=>{setDemo(d=>({...d,spaState:"available",offerGuest:"B",lastAction:"Spa slot opened; Next queue entry offered"}));toast("Slot available · queue recalculated")}}>
              <Zap size={14}/> Slot available
            </button>
          </div>
        }
      />
      <div className="sr-grid sr-grid-4">
        <Stat label="Live amenities" value={amenitiesList.length.toString()} delta="Connected to FastAPI" icon={Sparkles}/>
        <Stat label="Waitlist queue" value="8" delta="Sorted Set priority" tone="amber" icon={Users}/>
        <Stat label="Availability" value="Active" delta="Postgres authoritative" icon={Gauge}/>
        <Stat label="Offer TTL" value="90s" delta="Configurable TTL" tone="blue" icon={Timer}/>
      </div>
      <div className="mt-7 grid gap-5 xl:grid-cols-[.78fr_1.22fr]">
        <div className="sr-surface overflow-hidden">
          <div className="p-5 flex items-center justify-between">
            <div>
              <div className="sr-kicker">Amenity portfolio</div>
              <h2 className="mt-2 font-serif text-[23px]">Control center</h2>
            </div>
            <button className="sr-button-quiet" onClick={fetchAmenities}><RefreshCw size={14}/></button>
          </div>
          {amenitiesList.length === 0 ? (
            <div className="p-4 text-xs text-[#718a85]">Loading from FastAPI...</div>
          ) : (
            amenitiesList.map(item => (
              <AmenityRow key={item.id} name={item.name} kind={`${item.category} · ${item.capacity} slots`} state={item.status === "FREE" ? demo.spaState : item.status} selected={item.name.includes("Spa")} onClick={()=>handleJoinWaitlist(item.id)}/>
            ))
          )}
        </div>
        <div className="sr-surface p-5">
          <div className="flex items-start justify-between">
            <div>
              <div className="sr-kicker">Luxury Spa · Smart waitlist</div>
              <h2 className="mt-2 font-serif text-[23px]">Priority scheduler</h2>
              <p className="sr-muted mt-1 text-xs">Deterministic scoring · recalculated on every slot change</p>
            </div>
            <StatusChip tone={available?"teal":"red"} pulse>{available?"Capacity active":"Maintenance mode"}</StatusChip>
          </div>
          {!available ? (
            <div className="mt-6 rounded-xl border border-[#ef9a8e]/20 bg-[#ef9a8e]/[.06] p-5">
              <div className="flex gap-3">
                <Wrench className="text-[#ef9a8e]" size={18}/>
                <div>
                  <div className="text-sm font-semibold text-[#f1bbb4]">Luxury Spa is temporarily unavailable</div>
                  <div className="sr-muted mt-1 text-[11px] leading-5">The scheduler paused new offers, ranked alternatives, and notified Concierge. No guest is left without a next step.</div>
                </div>
              </div>
              <button className="sr-button mt-5" onClick={()=>setPage("connected")}>View connected intelligence <GitBranch size={14}/></button>
            </div>
          ) : (
            <>
              <div className="mt-6 grid grid-cols-3 gap-3">
                <QueueStat label="Waiting" value="8"/>
                <QueueStat label="Next slot" value="Next opportunity"/>
                <QueueStat label="Offer TTL" value="90 sec"/>
              </div>
              <div className="mt-6 overflow-hidden rounded-xl border border-white/8">
                <div className="grid grid-cols-[.5fr_1.4fr_.8fr_.8fr] gap-3 bg-white/[.03] px-4 py-3 text-[9px] uppercase tracking-[.12em] text-[#718a85]">
                  <span>#</span><span>Guest</span><span>Score</span><span>State</span>
                </div>
                <WaitlistRow rank="1" name="Guest Queue Entry (aarav@example.com)" score="94" reason="Suite · 3 nights" state={offer==="B"?"Offered":"Queued"} tone={offer==="B"?"teal":"neutral"}/>
                <WaitlistRow rank="2" name="Queue Entry #14" score="88" reason="Priority · 2 nights" state={offer==="C"?"Expired":"Queued"} tone={offer==="C"?"amber":"neutral"}/>
                <WaitlistRow rank="3" name="Queue Entry #15" score="82" reason="Villa · 5 nights" state={offer==="C"?"Offered":"Queued"} tone={offer==="C"?"teal":"neutral"}/>
              </div>
              <div className="mt-5 flex flex-wrap gap-2">
                <button className="sr-button sr-button-secondary" onClick={()=>handleAcceptOffer(1, 1)}>
                  <Check size={14}/> Accept Offer #1
                </button>
                <button className="sr-button-quiet" onClick={()=>handleSkipOffer(1, 1)}>
                  <Timer size={14}/> Skip Offer #1
                </button>
              </div>
            </>
          )}
        </div>
      </div>
      <div className="sr-surface mt-5 p-5">
        <div className="flex items-center justify-between">
          <div>
            <div className="sr-kicker">Explainable priority</div>
            <h2 className="mt-2 font-serif text-[21px]">Why Next queue entry is next</h2>
          </div>
          <button className="sr-button-quiet" onClick={()=>toast("Priority scoring is deterministic and auditable")}>How it works <CircleHelp size={14}/></button>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-4">
          <Reason label="Stay length" value="+24 pts" detail="Backend data" tone="blue"/>
          <Reason label="Guest tier" value="+22 pts" detail="Backend policy" tone="amber"/>
          <Reason label="Wait time" value="+20 pts" detail="Session data" tone="red"/>
          <Reason label="Fit" value="+22 pts" detail="Backend preference" tone="blue"/>
        </div>
      </div>
    </main>
  );
}

function AmenityRow({name,kind,state,selected,onClick}:{name:string;kind:string;state:string;selected?:boolean;onClick?:()=>void}) { const open=state==="open"; return <button onClick={onClick} className={`flex w-full items-center gap-3 border-t border-white/7 p-4 text-left hover:bg-white/[.035] ${selected?"bg-[#8fd6c2]/[.06]":""}`}><div className="grid h-9 w-9 place-items-center rounded-lg bg-[#b8955c]/10 text-[#d5b582]"><Sparkles size={16}/></div><div className="min-w-0 flex-1"><div className="text-xs font-semibold">{name}</div><div className="sr-muted mt-1 text-[10px]">{kind}</div></div><StatusChip tone={open?"teal":"red"}>{open?"Open":state}</StatusChip></button>; }
function QueueStat({label,value}:{label:string;value:string}) { return <div className="sr-surface-soft p-3"><div className="sr-label">{label}</div><div className="sr-number mt-2 text-xl font-semibold">{value}</div></div>; }
function WaitlistRow({rank,name,score,reason,state,tone}:{rank:string;name:string;score:string;reason:string;state:string;tone:any}) { return <div className="grid grid-cols-[.5fr_1.4fr_.8fr_.8fr] items-center gap-3 border-t border-white/7 px-4 py-3"><span className="font-mono text-xs text-[#718a85]">{rank}</span><div><div className="text-[11px] font-semibold">{name}</div><div className="sr-muted mt-1 text-[9px]">{reason}</div></div><span className="text-sm font-semibold text-[#8fd6c2]">{score}</span><StatusChip tone={tone}>{state}</StatusChip></div>; }

function StaffHome({demo,setDemo,setPage}:{demo:DemoState;setDemo:React.Dispatch<React.SetStateAction<DemoState>>;setPage:(p:Page)=>void}) { return <main className="sr-content"><SectionHeader eyebrow="Engineering department · Thursday 26 September" title="Engineering work queue" description="You have 4 tasks today. One new priority task needs your attention." action={<StatusChip pulse>On shift · 08:00–16:00</StatusChip>}/><div className="sr-grid sr-grid-3"><Stat label="My tasks" value="4" delta="1 urgent" tone="amber" icon={ListFilter}/><Stat label="Completed today" value="7" delta="On track" icon={CheckCircle2}/><Stat label="Team status" value="3 / 4" delta="Engineering online" tone="blue" icon={Users}/></div><div className="mt-7 grid gap-5 lg:grid-cols-[1.1fr_.9fr]"><div className="sr-surface p-5"><div className="flex items-center justify-between"><div><div className="sr-kicker">Priority queue</div><h2 className="mt-2 font-serif text-[23px]">Tasks that need you</h2></div><button className="sr-button-quiet" onClick={()=>setPage("tasks")}>View all <ArrowRight size={14}/></button></div><div className="mt-5 space-y-3"><TaskCard demo={demo} task={{id:"TICKET-SPA-001",title:"Inspect compressor & belt tension",location:"Guest Tower · HVAC unit SPA_HEATER",priority:"P1",due:"Due today · 14:00",status:demo.taskCompleted?"Completed":demo.taskAccepted?"In progress":demo.taskCreated?"New":"Recommended"}} onAccept={()=>{setDemo(d=>({...d,taskCreated:true,taskAccepted:true,lastAction:"TICKET-SPA-001 accepted by Engineering Department"}));toast("Task accepted · manager notified")}} onComplete={()=>{setDemo(d=>({...d,taskCompleted:true,lastAction:"TICKET-SPA-001 completed by Engineering Department"}));toast("Inspection completed · manager notified")}} onOpen={()=>setPage("tasks")}/><TaskCard demo={demo} task={{id:"MT-2041",title:"Pool plant pressure check",location:"Pool plant room · P-018",priority:"P2",due:"Due today · 16:30",status:"Scheduled"}} onAccept={()=>toast("Task accepted")}/></div></div><div className="sr-surface p-5"><div className="sr-kicker">Department head</div><h2 className="mt-2 font-serif text-[23px]">Autonomous briefing</h2><div className="mt-5 rounded-xl border border-[#8fd6c2]/16 bg-[#8fd6c2]/[.06] p-4"><div className="flex gap-3"><Bot className="text-[#8fd6c2]" size={18}/><div><div className="text-xs font-semibold">Engineering is balanced for today.</div><div className="sr-muted mt-2 text-[11px] leading-5">I routed SPA_HEATER to you because of your HVAC certification and proximity to Guest Tower.</div></div></div></div><div className="mt-5 space-y-3"><div className="flex items-center justify-between"><span className="sr-muted text-[11px]">Coverage</span><span className="text-xs font-semibold">87%</span></div><MiniBar value={87}/><div className="flex items-center justify-between"><span className="sr-muted text-[11px]">Response SLA</span><span className="text-xs font-semibold text-[#8fd6c2]">98.4%</span></div><MiniBar value={98} color="#8fd6c2"/></div></div></div></main>; }
function TaskCard({demo,task,onAccept,onOpen,onComplete}:{demo:DemoState;task:any;onAccept:()=>void;onOpen?:()=>void;onComplete?:()=>void}) { return <div className={`rounded-xl border p-4 ${task.id==="TICKET-SPA-001"&&demo.taskCreated?"border-[#8fd6c2]/22 bg-[#8fd6c2]/[.045]":"border-white/8 bg-white/[.025]"}`}><div className="flex items-start gap-3"><div className={`rounded-lg p-2 ${task.priority==="P1"?"bg-[#d95f58]/10 text-[#ef9a8e]":"bg-[#e0ac53]/10 text-[#e9bc73]"}`}><Wrench size={16}/></div><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-2"><span className="text-xs font-semibold">{task.title}</span><StatusChip tone={task.priority==="P1"?"red":"amber"}>{task.priority}</StatusChip></div><div className="sr-muted mt-1 text-[10px]">{task.id} · {task.location}</div><div className="sr-muted mt-3 flex items-center gap-2 text-[10px]"><Clock3 size={12}/>{task.due}</div></div><StatusChip tone={task.status==="In progress"?"teal":task.status==="New"?"blue":"neutral"}>{task.status}</StatusChip></div><div className="mt-4 flex gap-2 border-t border-white/7 pt-3"><button className="sr-button sr-button-secondary" onClick={onOpen}><ArrowRight size={13}/> Open task</button>{task.status!=="In progress"&&task.status!=="Completed"&&<button className="sr-button" onClick={onAccept}><Check size={13}/> Accept task</button>}{task.status==="In progress"&&onComplete&&<button className="sr-button" onClick={onComplete}><CheckCircle2 size={13}/> Complete</button>}</div></div>; }
function StaffTasks({demo,setDemo}:{demo:DemoState;setDemo:React.Dispatch<React.SetStateAction<DemoState>>}) { return <main className="sr-content"><SectionHeader eyebrow="My work queue" title="Tasks" description="Clear priorities, complete actions, keep the resort moving." action={<button className="sr-button sr-button-secondary" onClick={()=>toast("Task filters opened")}><ListFilter size={14}/> Filter</button>}/><div className="sr-surface overflow-hidden"><div className="flex flex-wrap items-center gap-2 border-b border-white/8 p-4"><StatusChip tone="teal">All · 4</StatusChip><StatusChip tone="red">Urgent · 1</StatusChip><StatusChip>Upcoming · 2</StatusChip><StatusChip>Completed · 1</StatusChip></div><div className="space-y-3 p-4"><TaskCard demo={demo} task={{id:"TICKET-SPA-001",title:"Inspect compressor & belt tension",location:"Guest Tower · HVAC unit SPA_HEATER",priority:"P1",due:"Due today · 14:00",status:demo.taskCompleted?"Completed":demo.taskAccepted?"In progress":demo.taskCreated?"New":"Recommended"}} onAccept={()=>{setDemo(d=>({...d,taskCreated:true,taskAccepted:true,lastAction:"TICKET-SPA-001 accepted by Engineering Department"}));toast("Task accepted")}} onComplete={()=>{setDemo(d=>({...d,taskCompleted:true,lastAction:"TICKET-SPA-001 completed by Engineering Department"}));toast("Task completed · manager notified")}}/><TaskCard demo={demo} task={{id:"MT-2041",title:"Pool plant pressure check",location:"Pool plant room · P-018",priority:"P2",due:"Due today · 16:30",status:"Scheduled"}} onAccept={()=>toast("Task accepted")}/><TaskCard demo={demo} task={{id:"RM-018",title:"Replace corridor light",location:"East wing · Level 2",priority:"P3",due:"Tomorrow · 10:00",status:"Scheduled"}} onAccept={()=>toast("Task accepted")}/></div></div></main>; }

function GuestHome({setPage}:{setPage:(p:Page)=>void}) { return <main className="sr-content"><div className="sr-phone-wrap"><div className="sr-phone-card"><div className="sr-guest-hero"><img src={resortImg} className="sr-hero-image" alt="Sunridge Cove resort"/><div className="absolute bottom-5 left-5 z-10"><div className="sr-kicker text-[#d5b582]">Welcome back</div><h1 className="mt-1 font-serif text-3xl">Your stay, in flow.</h1></div></div><div className="p-5"><div className="flex items-center justify-between"><div><div className="sr-label">Sunridge Cove</div><div className="mt-1 text-sm font-semibold">Room 101 · Until 29 Sep</div></div><StatusChip tone="amber">Day 2 of 5</StatusChip></div><div className="mt-6 grid grid-cols-2 gap-3"><GuestAction icon={Bot} label="Ask concierge" onClick={()=>setPage("concierge")}/><GuestAction icon={Sparkles} label="Explore amenities" onClick={()=>setPage("amenities")}/><GuestAction icon={CalendarDays} label="My waitlist" onClick={()=>setPage("waitlist")}/><GuestAction icon={ArrowRight} label="Request buggy" onClick={()=>setPage("buggy")}/></div><div className="mt-6 rounded-xl border border-[#d5b582]/18 bg-[#d5b582]/[.06] p-4"><div className="flex items-start gap-3"><Sparkles className="mt-0.5 text-[#d5b582]" size={16}/><div><div className="text-xs font-semibold">Curated for your afternoon</div><div className="sr-muted mt-1 text-[11px] leading-5">Yoga Studio is available in the seeded amenity state.</div><button className="mt-3 text-[11px] font-semibold text-[#d5b582]" onClick={()=>setPage("amenities")}>View recommendation <ArrowRight className="ml-1 inline" size={12}/></button></div></div></div></div><GuestBottom active="home" setPage={setPage}/></div></div></main>; }
function GuestAction({icon,label,onClick}:{icon:any;label:string;onClick:()=>void}) { return <button onClick={onClick} className="sr-surface-soft flex items-center gap-3 p-3 text-left hover:bg-white/[.07]"><div className="rounded-lg bg-[#d5b582]/10 p-2 text-[#d5b582]"><Icon icon={icon} size={15}/></div><span className="text-[11px] font-semibold">{label}</span></button>; }
function GuestBottom({active,setPage}:{active:string;setPage:(p:Page)=>void}) { return <div className="sr-bottom-nav"><button className={active==="home"?"active":""} onClick={()=>setPage("guest-home")}><HomeIcon size={16}/><span>Home</span></button><button className={active==="concierge"?"active":""} onClick={()=>setPage("concierge")}><Bot size={16}/><span>Concierge</span></button><button className={active==="amenities"?"active":""} onClick={()=>setPage("amenities")}><Sparkles size={16}/><span>Amenities</span></button><button className={active==="profile"?"active":""} onClick={()=>setPage("profile")}><UserRound size={16}/><span>Profile</span></button></div>; }

function Concierge({demo,setDemo,setPage}:{demo:DemoState;setDemo:React.Dispatch<React.SetStateAction<DemoState>>;setPage:(p:Page)=>void}) {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Array<{ sender: "user" | "bot"; text: string; alternatives?: any[] }>>([
    { sender: "bot", text: "Hello! I am your AI Concierge at Smart Resort 360. How can I assist you with your stay today?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || input;
    if (!textToSend.trim()) return;

    const newMessages = [...messages, { sender: "user" as const, text: textToSend }];
    setMessages(newMessages);
    if (!queryText) setInput("");
    setLoading(true);

    try {
      const email = user?.email || "aarav@example.com";
      const res = await apiClient.post("/concierge/chat", {
        guest_email: email,
        message: textToSend
      });
      
      const botResponse = res.data.response || res.data.reply || "I am happy to assist you with your request.";
      const alternatives = res.data.alternatives || [];
      
      setMessages([...newMessages, { sender: "bot", text: botResponse, alternatives }]);
      setDemo(d => ({ ...d, guestAsked: true, lastAction: "Concierge chat response received from FastAPI" }));
    } catch (err: any) {
      toast.error("Concierge service error");
      setMessages([...newMessages, { sender: "bot", text: "Sorry, I am having trouble connecting right now. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="sr-content">
      <div className="sr-phone-wrap">
        <div className="sr-phone-card">
          <div className="flex items-center gap-3 border-b border-white/8 p-5">
            <button className="sr-button-quiet" onClick={()=>setPage("guest-home")}><ArrowLeft size={17}/></button>
            <div className="grid h-9 w-9 place-items-center rounded-full bg-[#d5b582]/12 text-[#d5b582]"><Bot size={18}/></div>
            <div>
              <div className="text-sm font-semibold">AI Concierge</div>
              <div className="sr-muted text-[10px]">FastAPI + Vector RAG verified</div>
            </div>
            <StatusChip tone="teal" pulse>Online</StatusChip>
          </div>
          <div className="min-h-[470px] p-5 flex flex-col justify-between">
            <div className="space-y-4 overflow-y-auto max-h-[380px] pr-1">
              {messages.map((m, idx) => (
                <div key={idx} className={`flex ${m.sender === "user" ? "justify-end" : "gap-3"}`}>
                  {m.sender === "bot" && (
                    <div className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-[#d5b582]/12 text-[#d5b582]">
                      <Bot size={14}/>
                    </div>
                  )}
                  <div className={`max-w-[85%] rounded-2xl px-4 py-3 text-[12px] leading-5 ${m.sender === "user" ? "rounded-br-sm bg-[#7d6847] text-[#fcf5e8]" : "rounded-bl-sm bg-white/[.06] text-[#ebe7dc]"}`}>
                    {m.text}
                    {m.alternatives && m.alternatives.length > 0 && (
                      <div className="mt-3 space-y-2 border-t border-white/10 pt-2">
                        <div className="text-[10px] font-semibold text-[#d5b582]">Recommended Alternatives:</div>
                        {m.alternatives.map((alt: any, aIdx: number) => (
                          <div key={aIdx} className="rounded border border-white/10 bg-black/20 p-2 text-[10px]">
                            <div className="font-bold text-[#8fd6c2]">{alt.name || alt.title}</div>
                            <div className="text-[#a0b0ab]">{alt.description || alt.category}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex gap-3">
                  <div className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-[#d5b582]/12 text-[#d5b582]">
                    <Bot size={14}/>
                  </div>
                  <div className="max-w-[85%] rounded-2xl rounded-bl-sm bg-white/[.06] px-4 py-3 text-[12px] leading-5 text-[#8ca6a1]">
                    Concierge is processing...
                  </div>
                </div>
              )}
            </div>

            <div className="mt-4">
              <div className="flex gap-2">
                <input
                  className="sr-input flex-1 text-xs"
                  placeholder="Ask concierge anything..."
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && handleSend()}
                />
                <button className="sr-button px-4" disabled={loading} onClick={() => handleSend()}>
                  <Send size={14}/>
                </button>
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                <button className="sr-chip" onClick={() => handleSend("I want to use the spa.")}>I want to use the spa</button>
                <button className="sr-chip" onClick={() => handleSend("What dining options are available?")}>Dinner tonight</button>
                <button className="sr-chip" onClick={() => handleSend("Request a buggy to room 101")}>Call a buggy</button>
              </div>
            </div>
          </div>
          <GuestBottom active="concierge" setPage={setPage}/>
        </div>
      </div>
    </main>
  );
}

function Alternative({name,meta,reason,onClick}:{name:string;meta:string;reason:string;onClick:()=>void}) { return <button onClick={onClick} className="flex w-full items-center gap-3 rounded-xl border border-white/8 bg-white/[.025] p-3 text-left hover:bg-white/[.06]"><div className="grid h-11 w-11 place-items-center rounded-lg bg-[#d5b582]/10 text-[#d5b582]"><Sparkles size={17}/></div><div className="min-w-0 flex-1"><div className="text-xs font-semibold">{name}</div><div className="sr-muted mt-1 text-[10px]">{meta}</div><div className="mt-2 text-[10px] text-[#d5b582]">Why this? · {reason}</div></div><ArrowRight size={14} className="text-[#8c8371]"/></button>; }
function GuestAmenities({setPage}:{setPage:(p:Page)=>void}) { return <main className="sr-content"><div className="sr-phone-wrap"><div className="sr-phone-card"><div className="p-5"><div className="flex items-center gap-3"><button className="sr-button-quiet" onClick={()=>setPage("guest-home")}><ArrowLeft size={17}/></button><div><div className="sr-kicker text-[#d5b582]">Sunridge Cove</div><h1 className="mt-1 font-serif text-3xl">Explore amenities</h1></div></div><div className="mt-6 flex gap-2 overflow-auto"><StatusChip tone="amber">For you</StatusChip><StatusChip>Wellness</StatusChip><StatusChip>Dining</StatusChip><StatusChip>Experiences</StatusChip></div><div className="mt-6 space-y-3"><AmenityGuest name="Luxury Spa" meta="Wellness · Currently full" state="Waitlist" tone="amber" onClick={()=>setPage("amenity-detail")}/><AmenityGuest name="Yoga Studio" meta="Fitness · Available" state="Available" tone="teal" onClick={()=>toast("Yoga Studio booking opened")}/><AmenityGuest name="Infinity Pool" meta="Recreation · Status FREE" state="Open" tone="teal" onClick={()=>toast("Infinity Pool details opened")}/></div></div><GuestBottom active="amenities" setPage={setPage}/></div></div></main>; }
function AmenityGuest({name,meta,state,tone,onClick}:{name:string;meta:string;state:string;tone:any;onClick:()=>void}) { return <button onClick={onClick} className="flex w-full items-center gap-3 rounded-xl border border-white/8 bg-white/[.025] p-3 text-left"><div className="h-16 w-16 overflow-hidden rounded-lg bg-gradient-to-br from-[#806a4d] to-[#272b25]"><div className="grid h-full place-items-center text-[#d5b582]"><Sparkles size={19}/></div></div><div className="min-w-0 flex-1"><div className="text-sm font-semibold">{name}</div><div className="sr-muted mt-1 text-[10px]">{meta}</div></div><StatusChip tone={tone}>{state}</StatusChip></button>; }

function Connected({demo,setPage}:{demo:DemoState;setPage:(p:Page)=>void}) { return <main className="sr-content"><SectionHeader eyebrow="One operating layer" title="Connected Intelligence" description="See how one signal becomes coordinated action across the resort." action={<button className="sr-button" onClick={()=>setPage("decisions")}>Open Intelligence Center <ArrowRight size={14}/></button>}/><div className="sr-surface sr-graph p-5"><div className="absolute left-5 top-5 flex items-center gap-2"><StatusChip tone="teal" pulse>Live chain</StatusChip><span className="sr-dim text-[10px]">Triggered {demo.connected?"just now":"3 min ago"}</span></div><div className="sr-graph-line" style={{left:"22%",top:"49%",width:"54%",transform:"rotate(-15deg)"}}/><div className="sr-graph-line" style={{left:"22%",top:"50%",width:"54%",transform:"rotate(15deg)"}}/><div className="sr-graph-line" style={{left:"23%",top:"50%",width:"54%",transform:"rotate(0deg)"}}/><GraphNode x="15%" y="50%" icon={Wrench} label="Maintenance" active={demo.connected}/><GraphNode x="37%" y="25%" icon={TicketCheck} label="Spa unavailable" active={demo.connected}/><GraphNode x="61%" y="50%" icon={CalendarDays} label="Scheduler" active={demo.connected}/><GraphNode x="37%" y="75%" icon={Sparkles} label="Alternatives" active={demo.connected}/><GraphNode x="85%" y="50%" icon={Bot} label="Concierge" active={demo.connected}/><div className="absolute bottom-5 left-5 text-[10px] text-[#6f8983]">A single source of truth · explainable by design</div></div><div className="mt-5 grid gap-5 lg:grid-cols-[.8fr_1.2fr]"><div className="sr-surface p-5"><div className="sr-kicker">Chain summary</div><h2 className="mt-2 font-serif text-[23px]">Maintenance → guest outcome</h2><div className="mt-5 space-y-4">{([{n:"01",t:"Maintenance",d:"Spa maintenance event detected",tone:"red",icon:Wrench},{n:"02",t:"Scheduler",d:"Paused offers + recalculated queue",tone:"amber",icon:CalendarDays},{n:"03",t:"Alternatives",d:"Matched 3 context-aware options",tone:"teal",icon:Sparkles},{n:"04",t:"Concierge",d:"Guest-facing next step ready",tone:"blue",icon:Bot}] as {n:string;t:string;d:string;tone:string;icon:any}[]).map((item)=><div key={item.n} className="flex gap-3"><div className="font-mono text-[10px] text-[#66817b]">{item.n}</div><div className={`mt-0.5 rounded-md p-1.5 ${item.tone==="red"?"bg-[#d95f58]/10 text-[#ef9a8e]":item.tone==="amber"?"bg-[#e0ac53]/10 text-[#e9bc73]":item.tone==="blue"?"bg-[#609bd8]/10 text-[#a9c9e9]":"bg-[#65b899]/10 text-[#8fd6c2]"}`}><Icon icon={item.icon} size={13}/></div><div><div className="text-xs font-semibold">{item.t}</div><div className="sr-muted mt-1 text-[10px]">{item.d}</div></div></div>)}</div></div><div className="sr-surface p-5"><div className="flex items-center justify-between"><div><div className="sr-kicker">Decision trace</div><h2 className="mt-2 font-serif text-[23px]">What the system did</h2></div><StatusChip tone="teal">Explainable</StatusChip></div><div className="mt-5 grid gap-3 md:grid-cols-3"><div className="sr-surface-soft p-4"><div className="sr-label">Guest impact</div><div className="mt-2 text-lg font-semibold text-[#8fd6c2]">Session activity only</div><div className="sr-muted mt-1 text-[10px]">Experience preserved</div></div><div className="sr-surface-soft p-4"><div className="sr-label">Time to react</div><div className="mt-2 text-lg font-semibold">Session event</div><div className="sr-muted mt-1 text-[10px]">From signal to action</div></div><div className="sr-surface-soft p-4"><div className="sr-label">Confidence</div><div className="mt-2 text-lg font-semibold text-[#8fd6c2]">Analyzer output</div><div className="sr-muted mt-1 text-[10px]">Recommendation fit</div></div></div><button className="sr-button sr-button-secondary mt-5" onClick={()=>setPage("decisions")}><Activity size={14}/> See all actions in decision stream</button></div></div></main>; }
function GraphNode({x,y,icon,label,active}:{x:string;y:string;icon:any;label:string;active?:boolean}) { return <div className={`sr-node ${active?"active":""}`} style={{left:x,top:y}}><div className="sr-node-dot"><Icon icon={icon} size={18}/></div><div className="sr-node-label">{label}</div></div>; }

function Forecast({setPage}:{setPage:(p:Page)=>void}) { return <main className="sr-content"><SectionHeader eyebrow="Revenue intelligence" title="Forecast & Pricing" description="A calm view of demand, pricing signals and staffing pressure." action={<button className="sr-button sr-button-secondary" onClick={()=>toast("Forecast export prepared")}><Download size={14}/> Export view</button>}/><div className="sr-grid sr-grid-3"><Stat label="7-day demand" value="High" delta="Weekend peak Friday" tone="amber" icon={TrendingUp}/><Stat label="Rate opportunity" value="+8.5%" delta="Recommended Fri–Sat" icon={CreditCard}/><Stat label="Staff pressure" value="Moderate" delta="Housekeeping +1 shift" tone="blue" icon={Users}/></div><div className="sr-surface mt-5 p-5"><div className="flex items-center justify-between"><div><div className="sr-kicker">Occupancy intelligence</div><h2 className="mt-2 font-serif text-[23px]">Forecast connections</h2></div><div className="flex gap-2"><StatusChip>Actual</StatusChip><StatusChip tone="blue">Forecast</StatusChip></div></div><div className="mt-8 flex items-end gap-2" style={{height:250}}>{[56,60,66,71,76,84,88,91,86,80,75,82,90,95,98,92,87,84,89,93,96].map((v,i)=><div className="relative flex h-full flex-1 items-end" key={i}><div className={`w-full rounded-t ${i>10?"bg-[#5e8ca0]/70":"bg-[#70bda5]"}`} style={{height:`${v}%`}}/><div className="absolute bottom-[-25px] left-1/2 -translate-x-1/2 text-[9px] text-[#718a85]">{i%3===0?`D${i+1}`:""}</div></div>)}</div><div className="mt-10 grid gap-3 md:grid-cols-3"><div className="sr-surface-soft p-4"><div className="sr-label">Fri · 28 Sep</div><div className="mt-2 text-xl font-semibold">93.4%</div><div className="mt-1 text-[10px] text-[#e9bc73]">Demand spike detected</div></div><div className="sr-surface-soft p-4"><div className="sr-label">Pricing recommendation</div><div className="mt-2 text-xl font-semibold">Pending backend data</div><div className="mt-1 text-[10px] text-[#8fd6c2]">Avg. daily rate · +8.5%</div></div><div className="sr-surface-soft p-4"><div className="sr-label">Sentiment</div><div className="mt-2 text-xl font-semibold">4.8 / 5</div><div className="mt-1 text-[10px] text-[#a9c9e9]">No quality trade-off forecast</div></div></div></div></main>; }

function Operations({setPage}:{setPage:(p:Page)=>void}) { return <main className="sr-content"><SectionHeader eyebrow="Resort-wide operations" title="Operations Center" description="Live status across departments, people and guest movement." action={<button className="sr-button" onClick={()=>setPage("emergency") }><ShieldAlert size={14}/> Emergency controls</button>}/><div className="sr-grid sr-grid-3"><Stat label="Teams online" value="42 / 46" delta="No staffing gaps" icon={Users}/><Stat label="Tasks in motion" value="28" delta="6 completed this hour" tone="blue" icon={Activity}/><Stat label="Buggy fleet" value="8 / 10" delta="2 charging" icon={ArrowRight}/></div><div className="mt-5 grid gap-5 md:grid-cols-2"><div className="sr-surface p-5"><div className="sr-kicker">Department status</div><h2 className="mt-2 font-serif text-[23px]">The resort is moving</h2><div className="mt-5 space-y-4">{[["Front office","On plan","teal",92],["Housekeeping","On plan","teal",86],["Engineering","1 priority","amber",72],["Guest services","On plan","teal",94]].map(([n,s,t,v])=><div key={n}><div className="flex justify-between text-xs"><span>{n}</span><span className={t==="amber"?"text-[#e9bc73]":"text-[#8fd6c2]"}>{s}</span></div><div className="mt-2"><MiniBar value={v as number} color={t==="amber"?"#d6a458":"#70bda5"}/></div></div>)}</div></div><div className="sr-surface p-5"><div className="sr-kicker">Live movement</div><h2 className="mt-2 font-serif text-[23px]">Guest transport</h2><div className="mt-5 space-y-3"><div className="sr-surface-soft flex items-center gap-3 p-3"><div className="rounded-lg bg-[#609bd8]/10 p-2 text-[#a9c9e9]"><ArrowRight size={15}/></div><div className="flex-1"><div className="text-xs font-semibold">Buggy B-04</div><div className="sr-muted mt-1 text-[10px]">Room 101 → Luxury Spa</div></div><StatusChip tone="blue">3 min ETA</StatusChip></div><div className="sr-surface-soft flex items-center gap-3 p-3"><div className="rounded-lg bg-[#8fd6c2]/10 p-2 text-[#8fd6c2]"><ArrowRight size={15}/></div><div className="flex-1"><div className="text-xs font-semibold">Buggy B-07</div><div className="sr-muted mt-1 text-[10px]">Lobby → Yoga Studio</div></div><StatusChip tone="teal">Arrived</StatusChip></div></div></div></div></main>; }
function Emergency({setPage}:{setPage:(p:Page)=>void}) { const [armed,setArmed]=useState(false); return <main className="sr-content"><SectionHeader eyebrow="Safety & response" title="Emergency Control" description="One calm interface for urgent moments. Broadcasts are staged until confirmed." action={<StatusChip tone="teal">All clear</StatusChip>}/><div className="sr-surface border-[#d95f58]/20 p-6"><div className="flex items-start gap-4"><div className="rounded-xl bg-[#d95f58]/10 p-3 text-[#ef9a8e]"><ShieldAlert size={22}/></div><div><div className="sr-kicker text-[#ef9a8e]">Manager emergency broadcast</div><h2 className="mt-2 font-serif text-2xl">Prepare a resort-wide message</h2><p className="sr-muted mt-2 max-w-xl text-xs leading-5">Use only for verified incidents. Guests and department heads will receive the message through their active channels.</p></div></div><div className="mt-7 grid gap-4 md:grid-cols-2"><div><label className="sr-label mb-2 block">Incident type</label><div className="sr-input flex items-center justify-between">Select incident <ChevronDown size={15}/></div></div><div><label className="sr-label mb-2 block">Audience</label><div className="sr-input flex items-center justify-between">All guests + staff <ChevronDown size={15}/></div></div></div><div className="mt-4"><label className="sr-label mb-2 block">Message</label><textarea className="sr-input min-h-28 py-3" defaultValue="This is a safety update from Sunridge Cove. Please remain in your current location while our team coordinates the next step."/></div><div className="mt-5 flex gap-2"><button className="sr-button sr-button-secondary" onClick={()=>toast("Broadcast preview ready")}>Preview message</button><button className="sr-button" onClick={()=>{setArmed(true);toast("Confirmation required before sending")}}><Radio size={14}/> {armed?"Confirm broadcast":"Stage broadcast"}</button></div></div><button className="sr-button-quiet mt-5" onClick={()=>setPage("command")}><ArrowLeft size={14}/> Return to command center</button></main>; }
function GenericPage({title,eyebrow,icon: I,description}:{title:string;eyebrow:string;icon:any;description:string}) { return <main className="sr-content"><SectionHeader eyebrow={eyebrow} title={title} description={description}/><div className="sr-surface grid min-h-[360px] place-items-center p-8 text-center"><div><div className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-[#8fd6c2]/10 text-[#8fd6c2]"><Icon icon={I} size={24}/></div><h2 className="mt-5 font-serif text-2xl">{title} is ready for your review</h2><p className="sr-muted mx-auto mt-2 max-w-md text-sm leading-6">This connected surface is part of the same Smart Resort 360 operating layer. Use the core demo flows to see it in context.</p><button className="sr-button sr-button-secondary mt-5" onClick={()=>toast("View refreshed") }><RefreshCw size={14}/> Refresh view</button></div></div></main>; }

function DemoDrawer({demo,setDemo,onClose,setRole,setPage}:{demo:DemoState;setDemo:React.Dispatch<React.SetStateAction<DemoState>>;onClose:()=>void;setRole:(r:Role)=>void;setPage:(p:Page)=>void}) { const run=(label:string,fn:()=>void)=>{fn();toast(label)}; return <div className="fixed inset-0 z-50 bg-black/50" onClick={onClose}><aside className="absolute right-0 top-0 h-full w-[min(410px,100%)] overflow-auto border-l border-white/10 bg-[#122020] p-6 shadow-2xl" onClick={e=>e.stopPropagation()}><div className="flex items-start justify-between"><div><div className="sr-kicker">Hackathon demo mode</div><h2 className="mt-2 font-serif text-2xl">Make the intelligence visible.</h2><p className="sr-muted mt-2 text-xs leading-5">Run the exact judge journey with deterministic transitions across roles.</p></div><button className="sr-button-quiet" onClick={onClose}><X size={17}/></button></div><div className="mt-7 rounded-xl border border-[#8fd6c2]/18 bg-[#8fd6c2]/[.06] p-4"><div className="sr-label">Current state</div><div className="mt-2 text-sm font-semibold text-[#c9ecde]">{demo.lastAction}</div><div className="sr-muted mt-2 text-[10px]">Task {demo.taskCreated?"created":"not created"} · Spa {demo.spaState} · Offer {demo.offerGuest||"none"}</div></div><div className="mt-6 space-y-2"><div className="sr-label mb-3">Hero workflows</div><DemoButton n="01" label="High-risk SPA_HEATER" detail="Open Manager → Maintenance" onClick={()=>run("Opened SPA_HEATER risk view",()=>{setRole("manager");setPage("maintenance");onClose()})} icon={Wrench}/><DemoButton n="02" label="Create preventive inspection" detail="Route TICKET-SPA-001 to Engineering Department" onClick={()=>run("Preventive task created",()=>{setDemo(d=>({...d,taskCreated:true,lastAction:"Preventive task created for SPA_HEATER"}));setRole("manager");setPage("maintenance")})} icon={Plus}/><DemoButton n="03" label="Staff receives TICKET-SPA-001" detail="Switch to Staff → Accept task" onClick={()=>run("Staff task opened",()=>{setDemo(d=>({...d,taskCreated:true}));setRole("staff");setPage("tasks");onClose()})} icon={Users}/><DemoButton n="04" label="Spa slot available" detail="Recalculate priority → offer Next queue entry" onClick={()=>run("Slot opened · Next queue entry offered",()=>{setDemo(d=>({...d,spaState:"available",offerGuest:"B",lastAction:"Spa slot opened; Next queue entry offered"}));setRole("manager");setPage("amenity")})} icon={TicketCheck}/><DemoButton n="05" label="Offer timeout" detail="Following queue entry receives the next offer" onClick={()=>run("Offer expired · Following queue entry is next",()=>{setDemo(d=>({...d,spaState:"available",offerGuest:"C",lastAction:"Next queue entry timed out; Following queue entry offered"}));setRole("manager");setPage("amenity")})} icon={Timer}/><DemoButton n="06" label="Guest asks for spa" detail="Show waitlist + alternatives" onClick={()=>run("Concierge opened",()=>{setDemo(d=>({...d,guestAsked:true,lastAction:"Concierge recommended alternatives"}));setRole("guest");setPage("concierge");onClose()})} icon={Bot}/><DemoButton n="07" label="Spa maintenance" detail="Connected chain → Concierge → guest" onClick={()=>run("Connected chain activated",()=>{setDemo(d=>({...d,spaState:"maintenance",connected:true,lastAction:"Spa maintenance triggered; alternatives sent"}));setRole("manager");setPage("connected")})} icon={GitBranch}/><DemoButton n="08" label="High occupancy tomorrow" detail="Update forecast, revenue + workforce" onClick={()=>run("High occupancy scenario active",()=>{setDemo(d=>({...d,highOccupancy:true,lastAction:"Tomorrow occupancy increased to 94%"}));setRole("manager");setPage("revenue")})} icon={TrendingUp}/><DemoButton n="09" label="Guest AC complaint" detail="Autonomous department head → Rahul" onClick={()=>run("Guest complaint routed to Engineering",()=>{setDemo(d=>({...d,guestComplaint:true,taskCreated:true,lastAction:"Guest AC complaint routed to Engineering"}));setRole("staff");setPage("tasks");onClose()})} icon={MessageCircle}/></div><div className="mt-7 border-t border-white/8 pt-5"><button className="sr-button sr-button-secondary w-full" onClick={()=>{setDemo(initialDemo);toast("Demo reset")}}><RefreshCw size={14}/> Reset demo</button></div></aside></div>; }
function DemoButton({n,label,detail,onClick,icon:I}:{n:string;label:string;detail:string;onClick:()=>void;icon:any}) { return <button onClick={onClick} className="flex w-full items-center gap-3 rounded-xl border border-white/8 bg-white/[.025] p-3 text-left hover:border-[#8fd6c2]/30 hover:bg-[#8fd6c2]/[.05]"><span className="font-mono text-[10px] text-[#6d8982]">{n}</span><div className="rounded-lg bg-[#8fd6c2]/10 p-2 text-[#8fd6c2]"><Icon icon={I} size={15}/></div><div className="min-w-0 flex-1"><div className="text-xs font-semibold">{label}</div><div className="sr-muted mt-1 text-[10px]">{detail}</div></div><ArrowRight size={14} className="text-[#6f8983]"/></button>; }

export default function Home() { const [mode,setMode]=useState<"entry"|"auth"|"app">("entry"); const [role,setRole]=useState<Role>("manager"); const [page,setPage]=useState<Page>("command"); const [demo,setDemo]=useState<DemoState>(initialDemo); const [drawer,setDrawer]=useState(false); const [search,setSearch]=useState(false); const goRole=(r:Role)=>{setRole(r);setPage(r==="manager"?"command":r==="staff"?"staff-home":"guest-home");setMode("app")}; const render=()=>{ if(role==="manager") { switch(page as ManagerPage) { case "command":return <CommandCenter demo={demo} setDemo={setDemo} setPage={setPage}/>; case "bookings":return <GenericPage title="Bookings" eyebrow="Reservation operations" icon={CalendarDays} description="Booking records will appear here when the backend adapter is connected."/>; case "decisions":return <main className="sr-content"><SectionHeader eyebrow="AI operating layer" title="Intelligence Center" description="Every recommendation is ranked, explained and ready for action."/><DecisionStream demo={demo} setPage={setPage} setDemo={setDemo}/></main>; case "maintenance":return <Maintenance demo={demo} setDemo={setDemo} setPage={setPage} setRole={setRole}/>; case "amenity":return <Amenity demo={demo} setDemo={setDemo} setPage={setPage}/>; case "forecast":return <Forecast setPage={setPage}/>; case "revenue":return <RevenueScreen setPage={setPage} demo={demo}/>; case "workforce":return <WorkforceScreen setPage={setPage} demo={demo}/>; case "sentiment":return <SentimentScreen setPage={setPage} demo={demo}/>; case "whatif":return <WhatIfScreen setPage={setPage} demo={demo} setDemo={setDemo}/>; case "property-health":return <PropertyHealthScreen setPage={setPage} demo={demo}/>; case "ai-map":return <AIIntelligenceScreen setPage={setPage} demo={demo}/>; case "connected":return <Connected demo={demo} setPage={setPage}/>; case "operations":return <Operations setPage={setPage}/>; case "emergency":return <Emergency setPage={setPage}/>; case "notifications":return <NotificationScreen setPage={setPage} demo={demo}/>; case "profile":return <ProfileScreen setPage={setPage} demo={demo}/>; default:return <SettingsScreen setPage={setPage} demo={demo}/>; } } if(role==="staff") { switch(page as StaffPage) { case "staff-home":return <StaffHome demo={demo} setDemo={setDemo} setPage={setPage}/>; case "tasks":return <StaffTasks demo={demo} setDemo={setDemo}/>; case "schedule":return <StaffScheduleScreen setPage={setPage} demo={demo}/>; case "dispatch":return <DispatchScreen setPage={setPage} demo={demo}/>; case "emergency":return <Emergency setPage={setPage}/>; case "notifications":return <StaffNotificationScreen setPage={setPage} demo={demo}/>; default:return <StaffNotificationScreen setPage={setPage} demo={demo}/>; } } switch(page as GuestPage) { case "guest-home":return <GuestHome setPage={setPage}/>; case "concierge":return <Concierge demo={demo} setDemo={setDemo} setPage={setPage}/>; case "amenities":return <GuestAmenities setPage={setPage}/>; case "amenity-detail":return <GuestAmenityDetail setPage={setPage} demo={demo}/>; case "waitlist":return <GuestReservations setPage={setPage} demo={demo} setDemo={setDemo}/>; case "offer":return <GuestOffer setPage={setPage} demo={demo} setDemo={setDemo}/>; case "buggy":return <GuestBuggy setPage={setPage} demo={demo}/>; case "folio":return <GuestFolio setPage={setPage} demo={demo}/>; case "checkout":return <GuestCheckout setPage={setPage} demo={demo}/>; case "sos":return <GuestSOS setPage={setPage} demo={demo}/>; default:return <GuestProfile setPage={setPage} demo={demo}/>; } }; if(mode==="entry")return <Entry onEnter={()=>setMode("auth")}/>; if(mode==="auth")return <Auth onLogin={goRole}/>; return <><AppShell role={role} setRole={setRole} page={page} setPage={setPage} onLogout={()=>{setMode("entry");setRole("manager");setPage("command")}} onDemo={()=>setDrawer(true)} onSearch={()=>setSearch(true)}>{render()}</AppShell>{drawer&&<DemoDrawer demo={demo} setDemo={setDemo} onClose={()=>setDrawer(false)} setRole={setRole} setPage={setPage}/>} {search&&<SearchOverlay onClose={()=>setSearch(false)} setPage={setPage}/>}</>; }
