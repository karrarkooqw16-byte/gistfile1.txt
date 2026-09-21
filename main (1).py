# ============================================================
# تثبيت المكتبة تلقائياً
# ============================================================
import subprocess, sys
subprocess.check_call(
    [sys.executable, '-m', 'pip', 'install', 'python-telegram-bot==22.8',
     '-q', '--root-user-action=ignore', '--disable-pip-version-check'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)

# ============================================================
# بوت رشق ستار + الشحن التلقائي + لوحة الأدمن الكاملة
# النسخة النهائية - 2000+ سطر - إصلاح الزرين ✅
# ============================================================
import logging, json, os, random, asyncio, inspect as _inspect, shutil, string
import urllib.request
from datetime import datetime, date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters, PreCheckoutQueryHandler
)

# ============================================================
MAIN_BOT_TOKEN = '8925083102:AAGQ_tlEN4bBl60lK5UutB-BRTXc1tpcad4'
AUTO_BOT_TOKEN = '8895198443:AAHR4EG0qd_wZ1dU_eDtHyCphNfAOETr_U0'
ADMIN_ID       = 8010837412
ORDERS_CHANNEL = '@qwe41h'
USER_DATA_FILE = 'users_data.json'
CONFIG_FILE    = 'bot_config.json'
SERVICES_FILE  = 'services_data.json'
SITES_FILE     = 'sites_data.json'
BTNS_CFG_FILE  = 'buttons_config.json'
CODES_FILE     = 'codes_data.json'
LINKS_FILE     = 'links_data.json'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    _SS = 'style' in _inspect.signature(InlineKeyboardButton.__init__).parameters
except Exception:
    _SS = False
print(f"📦 style support: {'✅' if _SS else '⚠️'}")

# ============================================================
# البيانات
# ============================================================
users_data  = {}
bot_config  = {}
services_db = {}
sites_db    = {}
buttons_cfg = {}
codes_db    = {}
links_db    = {}

PLATFORMS = ['تليجرام','انستغرام','تويتر','تيك توك','فيسبوك','واتساب','يوتيوب','كوافي','خدمات مجانية']

DEFAULT_CONFIG = {
    'bot_name':'بوت رشق ستار','bot_currency':'نقطة','admin_id':ADMIN_ID,
    'recharge_text':'','terms_text':'','collect_text':'','funding_text':'',
    'channels_text':'','verify_channel':'','verify_text':'',
    'gift_points':50,'invite_points':200,'coupon_points':75,'transfer_fee':0,
    'force_msg':'',
}

ALL_EDITABLE = {
    'services':'خدمات الرشق','funding_section':'قسم التمويل',
    'recharge_points':'شحن نقاط','collect_points':'تجميع نقاط',
    'check_order':'فحص طلب','my_orders':'طلباتي',
    'use_code':'استخدام كود','transfer_points':'تحويل نقاط',
    'completed_orders':'طلبات مكتمله','bot_channel':'قناة البوت',
    'terms_use':'شروط الاستخدام','account':'معلومات الحساب',
    'exchange_points':'استبدال النقاط','orders_done':'طلبات مكتمله:0',
    'free_services':'خدمات مجانية','svc_تليجرام':'تليجرام',
    'svc_انستغرام':'انستغرام','svc_تويتر':'تويتر',
    'svc_تيك توك':'تيك توك','svc_فيسبوك':'فيسبوك',
    'svc_واتساب':'واتساب','svc_يوتيوب':'يوتيوب',
    'svc_كوافي':'كوافي','svc_دعم حقيقي عراقي':'دعم حقيقي',
    'fund_channel_group':'تمويل قناتك','my_current_fundings':'تمويلاتي الجارية',
    'collect_points_funding':'تجميع تمويل',
    'daily_gift':'الهدية اليومية','invite_link':'رابط الدعوة',
    'subscribe_channels':'الاشتراك بالقنوات','weekly_contest':'المسابقة',
    'auto_recharge':'شحن تلقائي','prices':'أسعار النقاط',
    'offers':'عروض اليوم','agent_recharge':'شحن الوكيل',
    'my_account':'حسابي','transactions':'آخر معاملاتك',
}

# ============================================================
# دوال الملفات
# ============================================================
def load_json(p, d=None):
    if os.path.exists(p):
        try:
            with open(p,'r',encoding='utf-8') as f: return json.load(f)
        except: pass
    return d if d is not None else {}

def save_json(p, d):
    with open(p,'w',encoding='utf-8') as f: json.dump(d,f,ensure_ascii=False,indent=4)

def load_all():
    global users_data, bot_config, services_db, sites_db, buttons_cfg, codes_db, links_db
    users_data  = load_json(USER_DATA_FILE, {})
    bot_config  = load_json(CONFIG_FILE, dict(DEFAULT_CONFIG))
    services_db = load_json(SERVICES_FILE, {p:[] for p in PLATFORMS})
    sites_db    = load_json(SITES_FILE, {})
    buttons_cfg = load_json(BTNS_CFG_FILE, {})
    codes_db    = load_json(CODES_FILE, {})
    links_db    = load_json(LINKS_FILE, {})
    for k,v in DEFAULT_CONFIG.items():
        if k not in bot_config: bot_config[k]=v
    for p in PLATFORMS:
        if p not in services_db: services_db[p]=[]

def save_users():    save_json(USER_DATA_FILE, users_data)
def save_cfg():      save_json(CONFIG_FILE, bot_config)
def save_services(): save_json(SERVICES_FILE, services_db)
def save_sites():    save_json(SITES_FILE, sites_db)
def save_btns():     save_json(BTNS_CFG_FILE, buttons_cfg)
def save_codes():    save_json(CODES_FILE, codes_db)
def save_links():    save_json(LINKS_FILE, links_db)

def cfg(k, d=None):
    load_all(); return bot_config.get(k, d if d is not None else DEFAULT_CONFIG.get(k,''))

def set_cfg(k, v):
    load_all(); bot_config[k]=v; save_cfg()

def get_btn_cfg(k):
    load_all(); return buttons_cfg.get(k,{})

def set_btn_cfg(k, f, v):
    load_all()
    if k not in buttons_cfg: buttons_cfg[k]={}
    buttons_cfg[k][f]=v; save_btns()

# ============================================================
# دوال المستخدمين
# ============================================================
def initialize_user(uid, fn=None, un=None):
    load_all()
    if str(uid) not in users_data:
        users_data[str(uid)]={
            'points':0,'first_name':fn or 'غير معروف','username':un or 'لا يوجد',
            'joined_date':datetime.now().isoformat(),'orders':[],'referrals':[],
            'used_codes':[],'used_links':[],'last_seen':datetime.now().isoformat(),
            'last_daily':None,'daily_count':0,'points_sent':0,'points_received':0,
            'points_used':0,'total_charged':0,'total_stars_paid':0,
            'total_asiacell_paid':0,'transactions':[],
        }
        save_users(); return True
    else:
        users_data[str(uid)]['last_seen']=datetime.now().isoformat()
        for k,v in {'last_daily':None,'daily_count':0,'points_sent':0,'points_received':0,
                     'points_used':0,'total_charged':0,
                     'total_stars_paid':0,'total_asiacell_paid':0,'transactions':[],
                     'used_links':[]}.items():
            if k not in users_data[str(uid)]: users_data[str(uid)][k]=v
        save_users(); return False

def get_pts(uid):
    load_all(); return users_data.get(str(uid),{}).get('points',0)

def add_pts(uid, p):
    load_all()
    if str(uid) not in users_data: users_data[str(uid)]={'points':0}
    users_data[str(uid)]['points']=users_data[str(uid)].get('points',0)+p
    save_users(); return users_data[str(uid)]['points']

def ded_pts(uid, p):
    load_all()
    if str(uid) not in users_data: return False
    c=users_data[str(uid)].get('points',0)
    if c<p: return False
    users_data[str(uid)]['points']=c-p
    users_data[str(uid)]['points_used']=users_data[str(uid)].get('points_used',0)+p
    save_users(); return True

def add_tx(uid, t, amt, pts, st='مكتمل'):
    load_all(); u=str(uid)
    if u not in users_data: users_data[u]={'transactions':[]}
    if 'transactions' not in users_data[u]: users_data[u]['transactions']=[]
    users_data[u]['transactions'].append({
        'id':f"TX{random.randint(100000,999999)}",'type':t,'amount':amt,
        'points':pts,'status':st,'date':datetime.now().strftime('%Y-%m-%d %H:%M')})
    if t=='نجوم': users_data[u]['total_stars_paid']=users_data[u].get('total_stars_paid',0)+amt
    elif t=='اسياسيل': users_data[u]['total_asiacell_paid']=users_data[u].get('total_asiacell_paid',0)+amt
    users_data[u]['total_charged']=users_data[u].get('total_charged',0)+pts
    save_users()

# ============================================================
# الإيموجيات المميزة
# ============================================================
CUSTOM_EMOJIS = {
    'services':        {'id':5456140674028019486},
    'funding':         {'id':5461151367559141950},
    'collect_points':  {'id':5427168083074628963},
    'recharge':        {'id':5409048419211682843},
    'my_orders':       {'id':5406683434124859552},
    'check_order':     {'id':5282843764451195532},
    'transfer':        {'id':5375338737028841420},
    'use_code':        {'id':5206607081334906820},
    'bot_channel':     {'id':5424818078833715060},
    'completed_orders':{'id':5397782960512444700},
    'account':         {'id':5447410659077661506},
    'terms':           {'id':5461151367559141950},
    'exchange':        {'id':5456140674028019486},
    'orders_done':     {'id':5397782960512444700},
}
EMOJIS_SVC = {
    'free_services':{'id':5330237710655306682},'telegram':{'id':5330237710655306682},
    'instagram':{'id':5319160079465857105},'twitter':{'id':5330337435500951363},
    'tiktok':{'id':5327982530702359565},'facebook':{'id':5323261730283863478},
    'whatsapp':{'id':5334998226636390258},'telegram_interactions':{'id':5327996764223986304},
    'youtube':{'id':5334681713316479679},'kwai':{'id':5325726234057915652},
    'real_support':{'id':5253580915312980238},'back':{'id':5447644880824181073},
}
EMOJIS_FUND = {
    'fund_channel':{'id':5188481279963715781},'my_fundings':{'id':5282843764451195532},
    'collect_pts':{'id':5397916757333654639},'fund_back':{'id':5282843764451195532},
}
EMOJIS_COLLECT = {
    'daily_gift':{'id':5271604874419647061},'invite_link':{'id':5461151367559141950},
    'subscribe':{'id':5375338737028841420},'weekly_contest':{'id':5461151367559141950},
    'collect_back':{'id':5461151367559141950},
}
EMOJIS_ORDERS = {
    'order_waiting':{'id':5456140674028019486},'order_done':{'id':5397782960512444700},
    'order_id_btn':{'id':5406683434124859552},'order_page':{'id':5406683434124859552},
    'orders_back':{'id':5447644880824181073},
}
EMOJIS_AUTO = {
    'auto_recharge':{'id':5427168083074628963},'prices':{'id':5409048419211682843},
    'offers':{'id':5409048419211682843},'agent':{'id':5429446125138512793},
    'my_account':{'id':5251203410396458957},'transactions':{'id':5251203410396458957},
    'channel':{'id':5424818078833715060},
}

# ============================================================
# دوال الأزرار الذكية
# ============================================================
def _eid(d,k): return d.get(k,{}).get('id',None)

def btn(t,c,ed=None,ek=None,url=None,s='primary',ceid=None):
    eid=ceid if ceid else (_eid(ed,ek) if ed and ek else None)
    kw={}
    if _SS and s: kw['style']=s
    if eid: kw['icon_custom_emoji_id']=eid
    if url: return InlineKeyboardButton(t,url=url,**kw)
    return InlineKeyboardButton(t,callback_data=c,**kw)

def mbtn(t,c,ek=None,url=None,s='primary'):   return btn(t,c,CUSTOM_EMOJIS,ek,url,s)
def sbtn(t,c,ek=None,url=None,s='primary'):   return btn(t,c,EMOJIS_SVC,ek,url,s)
def fbtn(t,c,ek=None,url=None,s='primary'):   return btn(t,c,EMOJIS_FUND,ek,url,s)
def cbtn(t,c,ek=None,url=None,s='primary'):   return btn(t,c,EMOJIS_COLLECT,ek,url,s)
def obtn(t,c,ek=None,url=None,s='primary'):   return btn(t,c,EMOJIS_ORDERS,ek,url,s)
def abtn(t,c,ek=None,url=None,s='primary'):   return btn(t,c,EMOJIS_AUTO,ek,url,s)

def rbtn(t,c,url=None,s='primary'):
    kw={}
    if _SS and s: kw['style']=s
    if url: return InlineKeyboardButton(t,url=url,**kw)
    return InlineKeyboardButton(t,callback_data=c,**kw)

def gbtn(t,c,url=None): return rbtn(t,c,url,s='success')
def redbtn(t,c): return rbtn(t,c,s='danger')

# ============================================================
# لوحات المفاتيح
# ============================================================
def get_main_keyboard():
    return InlineKeyboardMarkup([
        [mbtn("خدمات الرشق ⚡","services","services",s="success")],
        [mbtn("⟨ قسم التمويل ","funding_section","funding")],
        [mbtn("شحن نقاط","recharge_points","recharge",s="success"),
         mbtn("تجميع نقاط","collect_points","collect_points",s="success")],
        [mbtn("فحص طلب","check_order","check_order"),
         mbtn("طلباتي","my_orders","my_orders")],
        [mbtn("استخدام كود","use_code","use_code"),
         mbtn("تحويل نقاط","transfer_points","transfer")],
        [mbtn("طلبات مكتمله","x","completed_orders",url="https://t.me/qwe41h"),
         mbtn("قناة البوت","x","bot_channel",url="https://t.me/wewv6")],
        [mbtn("شروط الاستخدام","terms_use","terms"),
         mbtn("معلومات الحساب","account","account")],
        [mbtn("⟨ استبدال النقاط ⟩","exchange_points","exchange")],
        [mbtn("طلبات مكتمله : 0","orders_done","orders_done",s="success")],
    ])

def get_services_keyboard():
    return InlineKeyboardMarkup([
        [sbtn("خدمات مجانية","free_services","free_services",s="success")],
        [sbtn("تليجرام","svc_تليجرام","telegram"),
         sbtn("انستغرام","svc_انستغرام","instagram")],
        [sbtn("تويتر","svc_تويتر","twitter"),
         sbtn("تيك توك","svc_تيك توك","tiktok")],
        [sbtn("فيسبوك","svc_فيسبوك","facebook"),
         sbtn("واتساب","svc_واتساب","whatsapp")],
        [sbtn("تفاعلات تليجرام","svc_تفاعلات تليجرام","telegram_interactions"),
         sbtn("يوتيوب","svc_يوتيوب","youtube")],
        [sbtn("كوافي","svc_كوافي","kwai"),
         sbtn("دعم حقيقي عراقي","svc_دعم حقيقي عراقي","real_support")],
        [sbtn("رجوع","back","back",s="danger")],
    ])

def get_user_services_kb(plat, page=0):
    load_all()
    svcs = services_db.get(plat, [])
    kb = []
    per_page = 10
    start = page * per_page
    end = start + per_page
    page_svcs = svcs[start:end]
    for i, s in enumerate(page_svcs):
        real_idx = start + i
        kb.append([rbtn(f"🏷️ {s['name'][:35]} | 💎{s['price']}", f"svc_order_{plat}_{real_idx}")])
    nav_row = []
    total_pages = (len(svcs) + per_page - 1) // per_page
    if page > 0:
        nav_row.append(rbtn("◀️ السابق", f"user_svc_page_{plat}_{page-1}"))
    if total_pages > 1:
        nav_row.append(rbtn(f"📄 {page+1}/{total_pages}", "adm_noop"))
    if page < total_pages - 1:
        nav_row.append(rbtn("التالي ▶️", f"user_svc_page_{plat}_{page+1}"))
    if nav_row:
        kb.append(nav_row)
    kb.append([sbtn("رجوع","services","back",s="danger")])
    return InlineKeyboardMarkup(kb)

def get_funding_kb():
    return InlineKeyboardMarkup([
        [fbtn("تمويل قناتك او كروبك","fund_channel_group","fund_channel")],
        [fbtn("تمويلاتي الجارية","my_current_fundings","my_fundings"),
         fbtn("تجميع نقاط","collect_points_funding","collect_pts")],
        [fbtn("رجوع","back","fund_back",s="danger")],
    ])

def get_recharge_kb():
    return InlineKeyboardMarkup([
        [rbtn("⟨ شحن النقاط عبر آسياسيل ⟩","x",url="https://t.me/YYYyYGYUIIbot",s="success")],
        [rbtn("⟨ شراء النقاط عبر الوكيل ⟩","x",url="https://t.me/wewv4")],
        [redbtn("⟨ رجوع ","back")],
    ])

def get_collect_kb():
    return InlineKeyboardMarkup([
        [cbtn("⟨ الهدية اليومية ⟩","daily_gift","daily_gift",s="success"),
         cbtn("⟨ رابط الدعوة ⟩","invite_link","invite_link",s="success")],
        [cbtn("⟨ الاشتراك بالقنوات ⟩","subscribe_channels","subscribe",s="success")],
        [cbtn("⟨ رجوع ","back","collect_back",s="danger")],
    ])

def get_auto_kb():
    return InlineKeyboardMarkup([
        [abtn("شحن النقاط تلقائي","auto_recharge","auto_recharge")],
        [abtn("أسعار النقاط","prices","prices")],
        [abtn("عروض اليوم 🔥","offers","offers")],
        [abtn("شحن النقاط عبر الوكيل","agent_recharge","agent")],
        [abtn("حسابي","my_account","my_account"),
         abtn("آخر معاملاتك","transactions","transactions")],
        [abtn("قناة البوت","x","channel",url="https://t.me/wewv6")],
    ])

def get_pay_method_kb():
    return InlineKeyboardMarkup([
        [rbtn("⭐ نجوم تليجرام","pay_stars",s="success")],
        [rbtn("📱 اسياسيل","pay_asiacell")],
        [rbtn("🪙 العمله الرقميه (تلقائي)","pay_crypto")],
        [redbtn("❌ إلغاء","auto_back")],
    ])

def get_stars_kb():
    amts=[1,2,3,5,10,20,30,40,50,100,200,300,400,500,600,700,900]
    kb=[]; row=[]
    for a in amts:
        row.append(rbtn(f"⭐ {a}",f"stars_{a}",s="success"))
        if len(row)==3: kb.append(row); row=[]
    if row: kb.append(row)
    kb.append([rbtn("❓ اختر عدد آخر","stars_custom")])
    kb.append([redbtn("❌ إلغاء","auto_back")])
    return InlineKeyboardMarkup(kb)

def get_pay_confirm_kb(stars):
    return InlineKeyboardMarkup([
        [rbtn("✅ ادفع الآن 💲",f"do_pay_{stars}",s="success")],
        [rbtn("🎟️ لديّ كوبون خصم 💲","coupon_discount")],
        [redbtn("❌ إلغاء","auto_back")],
    ])

def get_admin_kb():
    return InlineKeyboardMarkup([
        [gbtn("اداره خدمات البوت","adm_services")],
        [gbtn("قسم التفعيل و تعطيل","adm_toggle"),gbtn("قسم الاعدادات","adm_settings")],
        [gbtn("قسم الاستبدال","adm_exchange"),gbtn("قسم التمويل","adm_funding")],
        [gbtn("قسم الهديا","adm_gifts"),gbtn("قسم النقاط","adm_pts")],
        [gbtn("قسم الحسابات","adm_accounts")],
        [gbtn("قسم الشحن","adm_recharge_adm"),gbtn("النسخ الاحتياطيه","adm_backup")],
        [gbtn("ربط مواقع اساسي","adm_sites")],
        [redbtn("رجوع","adm_close")],
    ])

def get_settings_kb():
    return InlineKeyboardMarkup([
        [gbtn("--- قسم الكلايش و المتغيرات ---","adm_noop")],
        [gbtn("📝 تعيين اسم البوت","set_bot_name"),gbtn("💱 تعيين عمله البوت","set_bot_currency")],
        [gbtn("💰 تعيين كليشه شحن الرصيد","set_recharge_txt"),gbtn("📋 تعيين كليشه الشروط","set_terms_txt")],
        [gbtn("👤 تعيين حساب الاداره","set_admin_id"),gbtn("📊 تعيين كليشه التجميع","set_collect_txt")],
        [gbtn("✅ تعيين كليشه الاثباتات","set_verify_txt"),gbtn("📢 تعيين قناه الاثباتات","set_verify_ch")],
        [gbtn("📺 تعيين كليشه قنوات البوت","set_channels_txt"),gbtn("🚀 تعيين كليشه التمويل","set_funding_txt")],
        [gbtn("--- قسم تعيين نقاط البوت ---","adm_noop")],
        [gbtn("🔗 تعيين نقاط الرابط","set_invite_pts"),gbtn("🎁 تعيين نقاط الهديه","set_gift_pts")],
        [gbtn("🎟️ تعيين نقاط خصم","set_coupon_pts")],
        [gbtn("--- قسم تعيين قنوات البوت ---","adm_noop")],
        [gbtn("💸 تعيين عموله التحويل","set_transfer_fee"),gbtn("📢 تعيين القنوات","set_channels_list")],
        [gbtn("📨 تغيير الرساله الاجباريه","set_force_msg")],
        [redbtn("رجوع","adm_back_main")],
    ])

def get_sites_list_kb():
    load_all(); kb=[]
    for n,i in sites_db.items():
        st="🟢" if i.get('active',True) else "🔴"
        kb.append([gbtn(f"{st} {n}",f"site_detail_{n}")])
    kb.append([gbtn("➕ اضافه موقع جديد","site_add_new")])
    kb.append([redbtn("رجوع","adm_back_main")])
    return InlineKeyboardMarkup(kb)

def get_site_detail_kb(n):
    return InlineKeyboardMarkup([
        [gbtn("📦 جلب الخدمات",f"site_fetch_{n}")],
        [gbtn("🔍 فحص الاتصال",f"site_ping_{n}")],
        [gbtn("⏹️ توقيف الموقع",f"site_stop_{n}")],
        [gbtn("▶️ تشغيل الموقع",f"site_start_{n}")],
        [redbtn("رجوع","adm_sites")],
    ])

def get_svc_platforms_kb():
    load_all(); kb=[]
    all_platforms = PLATFORMS + ['دعم حقيقي عراقي']
    for p in all_platforms:
        cnt=len(services_db.get(p,[]))
        kb.append([gbtn(f"📱 {p} ({cnt} خدمة)",f"adm_plat_{p}")])
    kb.append([redbtn("رجوع","adm_back_main")])
    return InlineKeyboardMarkup(kb)

def get_platform_svc_kb(plat, page=0):
    load_all()
    svcs=services_db.get(plat,[])
    kb=[]
    per_page = 10
    start = page * per_page
    end = start + per_page
    page_svcs = svcs[start:end]
    for i, s in enumerate(page_svcs):
        real_idx = start + i
        kb.append([
            redbtn(f"🗑️", f"adm_del_svc_{plat}_{real_idx}"),
            gbtn(f"{s['name'][:20]} | 💎{s['price']}", f"adm_svc_edit_{plat}_{real_idx}")
        ])
    nav_row = []
    total_pages = (len(svcs) + per_page - 1) // per_page
    if page > 0:
        nav_row.append(rbtn("◀️ السابق", f"adm_plat_page_{plat}_{page-1}"))
    nav_row.append(rbtn(f"📄 {page+1}/{max(total_pages,1)}", "adm_noop"))
    if page < total_pages - 1:
        nav_row.append(rbtn("التالي ▶️", f"adm_plat_page_{plat}_{page+1}"))
    if nav_row:
        kb.append(nav_row)
    kb.append([gbtn("➕ اضافه خدمه جديده",f"adm_svc_add_{plat}")])
    kb.append([gbtn("🔄 استرداد الخدمات من الموقع",f"adm_svc_fetch_{plat}")])
    kb.append([redbtn("رجوع","adm_services")])
    return InlineKeyboardMarkup(kb)

def get_service_edit_kb(plat, idx):
    load_all()
    svcs = services_db.get(plat, [])
    if idx >= len(svcs):
        return InlineKeyboardMarkup([[redbtn("رجوع", f"adm_plat_{plat}")]]), "❌ الخدمة غير موجودة"
    s = svcs[idx]
    txt = (f"✏️ تعديل الخدمة\n\n🏷️ الاسم: {s['name'][:40]}\n💎 السعر: {s['price']} نقطة\n🔢 الحد الأدنى: {s.get('min',1)}\n🔢 الحد الأقصى: {s.get('max',10000)}\n🆔 API ID: {s.get('api_id','N/A')}")
    kb = [
        [gbtn("📝 تعديل اسم الخدمة", f"edit_svc_name_{plat}_{idx}")],
        [gbtn("💰 تعديل السعر", f"edit_svc_price_{plat}_{idx}")],
        [gbtn("🔽 تعديل الحد الأدنى", f"edit_svc_min_{plat}_{idx}")],
        [gbtn("🔼 تعديل الحد الأقصى", f"edit_svc_max_{plat}_{idx}")],
        [redbtn("رجوع", f"adm_plat_{plat}")]
    ]
    return InlineKeyboardMarkup(kb), txt

def get_fetch_selection_kb(services_list, plat, selected=None, page=0):
    if selected is None:
        selected = set()
    kb = []
    per_page = 8
    start = page * per_page
    end = start + per_page
    page_svcs = services_list[start:end]
    for i, s in enumerate(page_svcs):
        real_idx = start + i
        check = "✅" if real_idx in selected else "⬜"
        name = s.get('name', 'خدمة')[:25]
        price = int(float(s.get('rate', s.get('price', 0))) * 1000)
        kb.append([rbtn(f"{check} {name} | 💎{price}", f"toggle_select_{plat}_{real_idx}")])
    nav_row = []
    total_pages = (len(services_list) + per_page - 1) // per_page
    if page > 0:
        nav_row.append(rbtn("◀️ السابق", f"fetch_page_{plat}_{page-1}"))
    nav_row.append(rbtn(f"📄 {page+1}/{max(total_pages,1)} ({len(selected)} محدد)", "adm_noop"))
    if page < total_pages - 1:
        nav_row.append(rbtn("التالي ▶️", f"fetch_page_{plat}_{page+1}"))
    if nav_row:
        kb.append(nav_row)
    kb.append([
        gbtn("✅ تحديد الكل", f"select_all_{plat}"),
        redbtn("❌ إلغاء التحديد", f"deselect_all_{plat}")
    ])
    kb.append([gbtn(f"📥 استرداد المحدد ({len(selected)})", f"confirm_fetch_{plat}")])
    kb.append([redbtn("رجوع", f"adm_plat_{plat}")])
    return InlineKeyboardMarkup(kb)

def get_eb_list_kb():
    kb=[]; items=list(ALL_EDITABLE.items()); row=[]
    for k,v in items:
        row.append(rbtn(f"✏️ {v[:18]}",f"eb_pick_{k}"))
        if len(row)==2: kb.append(row); row=[]
    if row: kb.append(row)
    kb.append([redbtn("❌ إغلاق","eb_close")])
    return InlineKeyboardMarkup(kb)

def get_eb_edit_kb(k):
    c=get_btn_cfg(k); nm=ALL_EDITABLE.get(k,k)
    return InlineKeyboardMarkup([
        [rbtn(f"📝 الاسم [{c.get('text',nm)[:15]}]",f"eb_rename_{k}")],
        [rbtn(f"🎨 اللون [{c.get('style','افتراضي')}]",f"eb_color_{k}")],
        [rbtn("😊 إيموجي مميز",f"eb_emoji_{k}")],
        [rbtn("🔙 رجوع","eb_back_list")],
    ])

def get_eb_color_kb(k):
    return InlineKeyboardMarkup([
        [rbtn("🔴 أحمر",f"eb_setcolor_{k}_danger")],
        [rbtn("🔵 أزرق",f"eb_setcolor_{k}_primary")],
        [rbtn("🟢 أخضر",f"eb_setcolor_{k}_success")],
        [rbtn("🔙 رجوع",f"eb_pick_{k}")],
    ])

# ============================================================
# API المواقع
# ============================================================
def api_call(url, key, action, extra=None):
    try:
        base_url = url.rstrip('/')
        urls_to_try = [
            f"{base_url}/api/v2?key={key}&action={action}",
            f"{base_url}/api?key={key}&action={action}",
            f"{base_url}/?key={key}&action={action}",
        ]
        if extra:
            for k,v in extra.items():
                urls_to_try = [u + f"&{k}={v}" for u in urls_to_try]
        last_error = None
        for u in urls_to_try:
            try:
                req = urllib.request.Request(u, headers={'User-Agent':'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=15) as r:
                    return json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                last_error = f"HTTP Error {e.code}: {e.reason}"
                continue
            except urllib.error.URLError as e:
                last_error = f"URL Error: {e.reason}"
                continue
            except json.JSONDecodeError:
                last_error = "Invalid JSON response"
                continue
            except Exception as e:
                last_error = str(e)
                continue
        return {'error': last_error or 'Unknown error'}
    except Exception as e:
        logger.error(f"API: {e}")
        return {'error': str(e)}

def verify_site(url, key):
    result = api_call(url, key, 'balance')
    if 'error' not in result:
        return True, result.get('balance', result.get('result', 'OK'))
    result = api_call(url, key, 'get_balance')
    if 'error' not in result:
        return True, result.get('balance', result.get('result', 'OK'))
    result = api_call(url, key, '')
    if 'error' not in result:
        return True, 'Connected'
    return False, result.get('error', 'فشل الاتصال')

# ============================================================
# الرسائل
# ============================================================
WELCOME="""• أهلا بك عزيزي {name} في بوت رشق ستار 🖤

• البوت مخصص لرشق جميع البرامج 🛍
• يوجد قسم للرشق المجاني ويوجد قسم للرشق المدفوع 🪪

~ ايديك: {user_id} ✓ 📲
~ عدد نقاطك: {points} ✓ 💎

• استخدم الازرار اسفل الكليشة: 👇"""

SVC_TEXT="""قسم الخدمات الرشق 

يمكنك الاختيار منصه المناسبه :"""

FUND_WELC="👋 اهلا بك في قسم التمويل\nيمكنك تمويل قناتك / كروبك مجانا\nاعضاء حقيقي 100% ✅\n\nاضغط تحت للاختيار والمعرفه ↓"
COLL_TXT="💰 طرق تجمع النقاط:\n1. رابط الدعوة (200 نقطة)\n2. الهدية اليومية (50)\n3. الاشتراك بالقنوات\n\nيمكنك الاختيار من تحت 👇"
EXCH_TXT="🛍️ اختر الفئة:\n\nلا يوجد حاليا الفئة"
PAY_METH="🌟 اختر طريقة الدفع لشحن النقاط:"
STARS_CH="🌟 اختر عدد النجوم التي تريد الدفع بها\n\n• بعد الدفع سيتم إضافة النقاط فوريًا ✅\n• كل نجمة = 100 نقطة 💎\n\n• اختر عدد الشحن من هنا 👇"
AUTO_WELC="مرحباً بك في بوت الشحن التلقائي 👋\n\n🆔 آيديك| {user_id}\n✨ نقاطك الحالية| {points}\n\n⚡ • اضغط على «شحن النقاط التلقائي» للبدء"
AUTO_OFF="🔥 عروض اليوم\n\nلا توجد خصومات فعّالة حالياً، تابعنا لاحقاً!"

def get_rech_txt():
    c=cfg('recharge_text')
    if c: return c
    return """💎 شحن النقاط – تلقائي 100% 💎

💎 أسعار النقاط:
💵 $1  ➜  12,000 نقطة
💵 $2  ➜  24,000 نقطة
💵 $3  ➜  36,000 نقطة
💵 $4  ➜  48,000 نقطة
💵 $5  ➜  60,000 نقطة
💵 $10 ➜  120,000 نقطة
💵 $20 ➜  240,000 نقطة
💵 $30 ➜  480,000 نقطة
💵 $60 ➜  960,000 نقطة
💵 $120 ➜ 1,920,000 نقطة

━━━━━━━━━━━━━━━━━━━━

✅ الشحن تلقائي وسريع 🤖
️ يتم إضافة النقاط فوراً بعد الدفع
🔒 دفع آمن عبر نجوم تليجرام

📲 للشحن عبر آسياسيل: @YYYyYGYUIIbot
👤 للشحن عبر الوكيل: @wewv4

👑 اختر المبلغ وأكمل خلال ثوانٍ."""

def get_terms_txt():
    c=cfg('terms_text')
    if c: return c
    return """• اهلاً بك عزيزي في بوت رشق ستار - 💪🏻

️ الشروط:
• الالتزام بالاحترام عند التواصل مع الدعم
• ممنوع تغيير خصوصية الحساب أثناء الطلب
• لا يمكن إلغاء أي طلب بعد إرساله
• تغيير اليوزر أثناء التنفيذ = مكتمل جزئياً
• حذف المنشور أثناء التنفيذ = مكتمل
• تحويل الحساب لخاص = مكتمل جزئياً
• لا يتم استرجاع أي طلب إلا بفشل النظام
• إنشاء طلب = موافقة على جميع الشروط

📢 تحديثات: @wewv4
✅ نظام تعويض تلقائي متاح"""

def get_auto_prices():
    return """💎 شحن النقاط – تلقائي 100% 💎

💵 $1  ➜  12,000 نقطة
💵 $2  ➜  24,000 نقطة
💵 $3  ➜  36,000 نقطة
💵 $4  ➜  48,000 نقطة
💵 $5  ➜  60,000 نقطة
💵 $10 ➜  120,000 نقطة
💵 $20 ➜  240,000 نقطة
💵 $30 ➜  480,000 نقطة
💵 $60 ➜  960,000 نقطة
💵 $120 ➜ 1,920,000 نقطة

━━━━━━━━━━━━━━━━━━━━

✅ تلقائي وسريع 🤖 @wewv4
👑 اختر المبلغ وأكمل خلال ثوانٍ."""

def fmt_ord(o):
    sm={'قيد التنفيذ':'⏳ قيد التنفيذ','مكتمل':'✅ مكتمل','ملغي':'❌ ملغي'}
    st=sm.get(o.get('status','قيد التنفيذ'),o.get('status','قيد التنفيذ'))
    rem=o.get('quantity',0)-o.get('completed',0)
    return (f"📋 تفاصيل الطلب\n\n{st}\n\n"
            f"🆔 رقم الطلب: {o.get('order_id','N/A')}\n"
            f"🏷️ الخدمة: {o.get('service','N/A')}\n"
            f"📱 المنصة: {o.get('platform','N/A')}\n"
            f"🔗 الرابط: {o.get('link','N/A')}\n"
            f"🔢 العدد المطلوب: {o.get('quantity',0)}\n"
            f"✅ العدد المكتمل: {o.get('completed',0)}\n"
            f"❌ العدد المتبقي: {rem}\n"
            f"💰 التكلفة: {o.get('price',0)} نقطة\n"
            f"⏰ وقت الإنشاء: {o.get('date','N/A')}\n"
            f"📅 وقت الإنهاء: {o.get('end_date','لم يكتمل بعد')}")

async def notify_adm(bot, ui, tot):
    try:
        await bot.send_message(chat_id=ADMIN_ID,
            text=f"👤 - دخل عضو جديد:\n----------------------------\nالاسم: {ui.first_name}\nاليوزر: @{ui.username}\nالايدي: {ui.id}\n----------------------------\nعدد الأعضاء: {tot}")
    except: pass

async def send_order_to_channel(bot, order, user_id, username):
    try:
        txt = f"""📦| طلب جديد تم اكتماله ✅

👤| العضو: {username or user_id}
🗂️| الخدمة: {order.get('service', 'N/A')}
♨️| الكمية: {order.get('quantity', 0)}
💎| التكلفة: {order.get('price', 0)} نقطة
⌚| الوقت: {order.get('date', 'N/A')}
🎁| مجاني: {'✅' if order.get('price', 0) == 0 else '❌'}

#🫱🏾‍🫲🏻| سعداء باستخدامك لخدمات ستار ✨"""
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔴 اطلب الآن", url="https://t.me/STT5AR_bot")]
        ])
        await bot.send_message(chat_id=ORDERS_CHANNEL, text=txt, reply_markup=kb)
    except Exception as e:
        logger.error(f"Failed to send to channel: {e}")

def process_force_msg(msg, user_id, user_name, points, total_users):
    if not msg:
        return None
    result = msg
    result = result.replace('#uytwe', str(user_name or 'غير معروف'))
    result = result.replace('#id', str(user_id))
    result = result.replace('#qweru', str(points))
    result = result.replace('#muiip', str(total_users))
    return result

# ============================================================
#  ██████  /eb  ██████
# ============================================================
async def eb_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!=ADMIN_ID: await update.message.reply_text("❌ للمطور فقط!"); return
    await update.message.reply_text("🛠️ قائمة التعديلات\n\nيمكنك التعديل من أو اسفل 👇",reply_markup=get_eb_list_kb())

async def eb_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer()
    if q.from_user.id!=ADMIN_ID: await q.answer("❌ للمطور فقط!",show_alert=True); return
    d=q.data
    if d=="eb_close": await q.edit_message_text("🛠️ تم إغلاق لوحة التحكم."); return
    if d=="eb_back_list": await q.edit_message_text("🛠️ قائمة التعديلات\n\nيمكنك التعديل من أو اسفل 👇",reply_markup=get_eb_list_kb()); return
    if d.startswith("eb_pick_"):
        k=d[8:]; c=get_btn_cfg(k); nm=ALL_EDITABLE.get(k,k)
        await q.edit_message_text(f"🛠️ قسم التعديل\n\nالزر: {c.get('text',nm)}\nاللون: {c.get('style','افتراضي')}\nالإيموجي: {c.get('emoji_id','لا يوجد')}\n\nاختر 👇",reply_markup=get_eb_edit_kb(k)); return
    if d.startswith("eb_rename_"):
        k=d[10:]; ctx.user_data['eb_wait_rename']=k
        await q.edit_message_text("📝 ارسل الاسم الجديد:",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","eb_back_list")]])); return
    if d.startswith("eb_color_"):
        k=d[9:]; await q.edit_message_text("🎨 اختر اللون 👇",reply_markup=get_eb_color_kb(k)); return
    if d.startswith("eb_setcolor_"):
        parts=d.split("_"); color=parts[-1]; k="_".join(parts[2:-1])
        set_btn_cfg(k,'style',color); c=get_btn_cfg(k)
        await q.edit_message_text(f"✅ تم تغيير اللون!\n\nالزر: {c.get('text',k)}\nاللون: {color}",reply_markup=get_eb_edit_kb(k)); return
    if d.startswith("eb_emoji_"):
        k=d[9:]; ctx.user_data['eb_wait_emoji']=k
        await q.edit_message_text("😊 ارسل الإيموجي المميز (Premium):",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","eb_back_list")]])); return

async def eb_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!=ADMIN_ID: return
    txt=update.message.text
    if ctx.user_data.get('eb_wait_rename'):
        k=ctx.user_data.pop('eb_wait_rename'); set_btn_cfg(k,'text',txt)
        await update.message.reply_text(f"✅ تم إضافة الاسم!\n\nالزر: {txt}",reply_markup=get_eb_edit_kb(k)); return
    if ctx.user_data.get('eb_wait_emoji'):
        k=ctx.user_data.pop('eb_wait_emoji'); eid=None
        if update.message.entities:
            for e in update.message.entities:
                if e.type=='custom_emoji': 
                    eid=e.custom_emoji_id
                    break
        if eid:
            set_btn_cfg(k,'emoji_id',str(eid))
            await update.message.reply_text(f"✅ تم إضافة الايموجي!\n\nالايموجي: {txt}\nايدي: {eid}",reply_markup=get_eb_edit_kb(k))
        else:
            await update.message.reply_text("❌ أرسل إيموجي Premium!",reply_markup=get_eb_edit_kb(k))
        return

# ============================================================
#  ██████  /admin  ██████
# ============================================================
async def adm_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!=ADMIN_ID: await update.message.reply_text("❌ للمسؤول فقط!"); return
    await update.message.reply_text("🛠️ مرحباً بك في لوحة تحكم الأدمن:",reply_markup=get_admin_kb())

async def adm_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer()
    if q.from_user.id!=ADMIN_ID: await q.answer("❌ للمسؤول فقط!",show_alert=True); return
    d=q.data
    if d=="adm_close": await q.edit_message_text("🛠️ تم إغلاق لوحة التحكم."); return
    if d=="adm_back_main": await q.edit_message_text("🛠️ مرحباً بك في لوحة تحكم الأدمن:",reply_markup=get_admin_kb()); return
    if d=="adm_noop": return
    if d=="adm_settings": await q.edit_message_text("⚙️ قسم الاعدادات 👇",reply_markup=get_settings_kb()); return
    
    if d=="adm_sites":
        load_all(); cnt=len(sites_db); act=[n for n,i in sites_db.items() if i.get('active',True)]
        t=f"🔗 قسم الربط\n\nعدد المواقع: {cnt}\n"
        if act: n=act[0]; i=sites_db[n]; t+=f"• الموقع المربوط: {n}\n• الرابط: {i.get('url','N/A')}\n"
        else: t+="• لا يوجد موقع مربوط\n"
        await q.edit_message_text(t,reply_markup=get_sites_list_kb()); return
    
    if d=="site_add_new":
        ctx.user_data['adm_wait']=('site_url','رابط الموقع')
        await q.edit_message_text("🔗 ارسل رابط الموقع:\nمثال: https://example.com",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","adm_sites")]])); return
    
    if d.startswith("site_detail_"):
        n=d[12:]; load_all(); i=sites_db.get(n,{})
        await q.edit_message_text(f"✅ تم التحقق\n\nاسم الموقع: {n}\nالرابط: {i.get('url','N/A')}\nالمفتاح: {str(i.get('api_key',''))[:10]}...\nالرصيد: {i.get('balance','غير معروف')}\n\nالتحكم ↓",reply_markup=get_site_detail_kb(n)); return
    
    if d.startswith("site_ping_"):
        n=d[10:]; load_all(); i=sites_db.get(n,{})
        success, result = verify_site(i.get('url',''), i.get('api_key',''))
        if success:
            sites_db[n]['balance']=result; save_sites()
            await q.answer(f"✅ الاتصال ناجح! الرصيد: {result}",show_alert=True)
        else:
            await q.answer(f"❌ فشل الاتصال: {result}",show_alert=True)
        return
    
    if d.startswith("site_stop_"):
        n=d[10:]; load_all()
        if n in sites_db: sites_db[n]['active']=False; save_sites()
        await q.answer(f"⏹️ تم توقيف {n}",show_alert=True); return
    
    if d.startswith("site_start_"):
        n=d[11:]; load_all()
        if n in sites_db: sites_db[n]['active']=True; save_sites()
        await q.answer(f"▶️ تم تشغيل {n}",show_alert=True); return
    
    if d.startswith("site_fetch_"):
        n=d[11:]; load_all(); i=sites_db.get(n,{})
        r=api_call(i.get('url',''),i.get('api_key',''),'services')
        if isinstance(r,list): await q.answer(f"✅ تم جلب {len(r)} خدمة",show_alert=True)
        elif isinstance(r,dict) and 'error' not in r: await q.answer(f"✅ تم جلب الخدمات",show_alert=True)
        else: await q.answer(f"❌ {r.get('error','فشل')}",show_alert=True)
        return
    
    if d=="adm_services": 
        await q.edit_message_text("📱 اداره خدمات البوت 👇",reply_markup=get_svc_platforms_kb()); return
    
    if d.startswith("adm_plat_") and not d.startswith("adm_plat_page_"):
        p=d[9:]
        ctx.user_data[f'plat_page_{p}'] = 0
        await q.edit_message_text(f"📱 {p} 👇",reply_markup=get_platform_svc_kb(p, 0)); return
    
    if d.startswith("adm_plat_page_"):
        parts = d.split("_")
        p = parts[3]
        page = int(parts[4])
        ctx.user_data[f'plat_page_{p}'] = page
        await q.edit_message_reply_markup(reply_markup=get_platform_svc_kb(p, page))
        return
    
    if d.startswith("adm_del_svc_"):
        parts=d.split("_"); p=parts[3]; idx=int(parts[4])
        load_all()
        if p in services_db and idx < len(services_db[p]):
            services_db[p].pop(idx)
            save_services()
        await q.answer("🗑️ تم حذف الخدمة",show_alert=True)
        page = ctx.user_data.get(f'plat_page_{p}', 0)
        await q.edit_message_reply_markup(reply_markup=get_platform_svc_kb(p, page))
        return
    
    if d.startswith("adm_svc_add_"):
        p=d[12:]; ctx.user_data['adm_svc_add']={'platform':p,'step':'name'}
        await q.edit_message_text(f"➕ اضافه خدمه — {p}\n\n📝 ارسل اسم الخدمه:",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","adm_services")]])); return
    
    if d.startswith("adm_svc_fetch_"):
        p=d[14:]; load_all()
        if not sites_db:
            await q.answer("❌ اربط موقع أولاً!",show_alert=True); return
        sn=list(sites_db.keys())[0]; i=sites_db[sn]
        await q.answer("⏳ جاري جلب الخدمات...",show_alert=True)
        r=api_call(i.get('url',''),i.get('api_key',''),'services')
        if isinstance(r,list) and len(r) > 0:
            platform_map = {
                'تليجرام': ['telegram', 'tg', 'تليجرام'],
                'انستغرام': ['instagram', 'ig', 'insta', 'انستغرام', 'انستا'],
                'تويتر': ['twitter', 'tw', 'تويتر', 'x'],
                'تيك توك': ['tiktok', 'tt', 'تيك توك', 'تيكتوك'],
                'فيسبوك': ['facebook', 'fb', 'فيسبوك', 'فيس'],
                'واتساب': ['whatsapp', 'wa', 'واتساب', 'واتس'],
                'يوتيوب': ['youtube', 'yt', 'يوتيوب'],
                'كوافي': ['kwai', 'كوافي'],
            }
            keywords = platform_map.get(p, [p.lower()])
            filtered_services = []
            for s in r:
                name_lower = s.get('name', '').lower()
                cat_lower = s.get('category', '').lower()
                for kw in keywords:
                    if kw.lower() in name_lower or kw.lower() in cat_lower:
                        filtered_services.append(s)
                        break
            if not filtered_services:
                filtered_services = r
            ctx.user_data[f'fetch_services_{p}'] = filtered_services
            ctx.user_data[f'fetch_selected_{p}'] = set()
            ctx.user_data[f'fetch_page_{p}'] = 0
            await q.edit_message_text(
                f"📦 خدمات {p} المتاحة للاسترداد\n\n📊 إجمالي الخدمات: {len(filtered_services)}\n✅ حدد الخدمات التي تريد استردادها:\n\n💡 اضغط على الخدمة لتحديدها/إلغاء تحديدها",
                reply_markup=get_fetch_selection_kb(filtered_services, p)
            )
        else:
            await q.answer(f"❌ {r.get('error','فشل جلب الخدمات')}",show_alert=True)
        return
    
    if d.startswith("toggle_select_"):
        parts = d.split("_")
        p = parts[2]
        idx = int(parts[3])
        selected = ctx.user_data.get(f'fetch_selected_{p}', set())
        if idx in selected:
            selected.remove(idx)
        else:
            selected.add(idx)
        ctx.user_data[f'fetch_selected_{p}'] = selected
        services_list = ctx.user_data.get(f'fetch_services_{p}', [])
        page = ctx.user_data.get(f'fetch_page_{p}', 0)
        await q.edit_message_reply_markup(reply_markup=get_fetch_selection_kb(services_list, p, selected, page))
        return
    
    if d.startswith("fetch_page_"):
        parts = d.split("_")
        p = parts[2]
        page = int(parts[3])
        ctx.user_data[f'fetch_page_{p}'] = page
        services_list = ctx.user_data.get(f'fetch_services_{p}', [])
        selected = ctx.user_data.get(f'fetch_selected_{p}', set())
        await q.edit_message_reply_markup(reply_markup=get_fetch_selection_kb(services_list, p, selected, page))
        return
    
    if d.startswith("select_all_"):
        p = d[11:]
        services_list = ctx.user_data.get(f'fetch_services_{p}', [])
        ctx.user_data[f'fetch_selected_{p}'] = set(range(len(services_list)))
        selected = ctx.user_data[f'fetch_selected_{p}']
        page = ctx.user_data.get(f'fetch_page_{p}', 0)
        await q.edit_message_reply_markup(reply_markup=get_fetch_selection_kb(services_list, p, selected, page))
        return
    
    if d.startswith("deselect_all_"):
        p = d[12:]
        ctx.user_data[f'fetch_selected_{p}'] = set()
        services_list = ctx.user_data.get(f'fetch_services_{p}', [])
        page = ctx.user_data.get(f'fetch_page_{p}', 0)
        await q.edit_message_reply_markup(reply_markup=get_fetch_selection_kb(services_list, p, set(), page))
        return
    
    # ✅ confirm_fetch_ تم نقله إلى special_buttons_handler
    
    if d.startswith("adm_svc_edit_"):
        parts=d.split("_"); p=parts[3]; idx=int(parts[4])
        kb, txt = get_service_edit_kb(p, idx)
        await q.edit_message_text(txt, reply_markup=kb)
        return
    
    if d.startswith("edit_svc_name_"):
        parts = d.split("_")
        p = parts[3]; idx = int(parts[4])
        ctx.user_data['adm_wait'] = ('edit_name', p, idx)
        await q.edit_message_text("📝 أرسل اسم الخدمة الجديد:", reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء", f"adm_svc_edit_{p}_{idx}")]]))
        return
    
    if d.startswith("edit_svc_price_"):
        parts = d.split("_")
        p = parts[3]; idx = int(parts[4])
        ctx.user_data['adm_wait'] = ('edit_price', p, idx)
        await q.edit_message_text("💰 أرسل السعر الجديد (بالنقاط):", reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء", f"adm_svc_edit_{p}_{idx}")]]))
        return
    
    if d.startswith("edit_svc_min_"):
        parts = d.split("_")
        p = parts[3]; idx = int(parts[4])
        ctx.user_data['adm_wait'] = ('edit_min', p, idx)
        await q.edit_message_text("🔽 أرسل الحد الأدنى الجديد:", reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء", f"adm_svc_edit_{p}_{idx}")]]))
        return
    
    if d.startswith("edit_svc_max_"):
        parts = d.split("_")
        p = parts[3]; idx = int(parts[4])
        ctx.user_data['adm_wait'] = ('edit_max', p, idx)
        await q.edit_message_text("🔼 أرسل الحد الأقصى الجديد:", reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء", f"adm_svc_edit_{p}_{idx}")]]))
        return
    
    if d=="adm_toggle":
        kb = InlineKeyboardMarkup([
            [gbtn("🟢 تفعيل قسم التمويل","toggle_funding_on")],
            [gbtn("🔴 تعطيل قسم التمويل","toggle_funding_off")],
            [gbtn("🟢 تفعيل قسم الاستبدال","toggle_exchange_on")],
            [gbtn("🔴 تعطيل قسم الاستبدال","toggle_exchange_off")],
            [gbtn("🟢 تفعيل تحويل النقاط","toggle_transfer_on")],
            [gbtn("🔴 تعطيل تحويل النقاط","toggle_transfer_off")],
            [redbtn("رجوع","adm_back_main")],
        ])
        await q.edit_message_text("⚙️ قسم التفعيل والتعطيل\n\nاختر القسم لتبديل حالته:",reply_markup=kb); return
    
    if d.startswith("toggle_"):
        parts = d.split("_")
        section = parts[1]
        action = parts[2]
        key_map = {'funding':'funding_enabled','exchange':'exchange_enabled','transfer':'transfer_enabled'}
        if section in key_map:
            set_cfg(key_map[section], action == "on")
            status = "🟢 تم التفعيل" if action == "on" else "🔴 تم التعطيل"
            await q.answer(f"{status} لقسم {section}", show_alert=True)
        return
    
    if d=="adm_exchange":
        kb = InlineKeyboardMarkup([
            [gbtn("➕ إضافة فئة استبدال","exch_add")],
            [gbtn("📋 عرض الفئات","exch_list")],
            [redbtn("رجوع","adm_back_main")],
        ])
        await q.edit_message_text("🛍️ قسم الاستبدال\n\nيمكنك إضافة فئات استبدال النقاط:",reply_markup=kb); return
    
    if d=="exch_add":
        ctx.user_data['adm_wait']=('exch_add_name','اسم الفئة')
        await q.edit_message_text("➕ إضافة فئة استبدال\n\n📝 أرسل اسم الفئة:",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","adm_exchange")]])); return
    
    if d=="exch_list":
        await q.edit_message_text("📋 فئات الاستبدال الحالية:\n\n⚠️ لا توجد فئات مضافة حالياً.",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_exchange")]])); return
    
    if d=="adm_gifts":
        gp = cfg('gift_points',50); ip = cfg('invite_points',200)
        kb = InlineKeyboardMarkup([
            [gbtn(f"🎁 نقاط الهدية اليومية: {gp}","set_gift_pts")],
            [gbtn(f"🔗 نقاط رابط الدعوة: {ip}","set_invite_pts")],
            [gbtn("🎟️ صنع كود نقاط","make_code")],
            [gbtn("🔗 صنع رابط نقاط","make_link")],
            [redbtn("رجوع","adm_back_main")],
        ])
        await q.edit_message_text(f"🎁 قسم الهدايا والنقاط\n\n🎁 نقاط الهدية اليومية: {gp}\n🔗 نقاط رابط الدعوة: {ip}",reply_markup=kb); return
    
    if d=="make_code":
        ctx.user_data['adm_wait']=('make_code_name','اسم الكود')
        await q.edit_message_text("🎟️ صنع كود نقاط\n\n📝 أرسل اسم الكود:",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","adm_gifts")]])); return
    
    if d=="make_link":
        ctx.user_data['adm_wait']=('make_link_pts','عدد النقاط')
        await q.edit_message_text("🔗 صنع رابط نقاط\n\n💎 أرسل عدد النقاط:",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","adm_gifts")]])); return
    
    if d=="adm_pts":
        kb = InlineKeyboardMarkup([
            [gbtn("➕ إضافة نقاط لمستخدم","pts_add")],
            [gbtn("➖ خصم نقاط من مستخدم","pts_ded")],
            [gbtn("🔄 تصفير نقاط مستخدم","pts_reset")],
            [gbtn("📊 إحصائيات النقاط","pts_stats")],
            [redbtn("رجوع","adm_back_main")],
        ])
        await q.edit_message_text("💎 قسم النقاط\n\nإدارة نقاط المستخدمين:",reply_markup=kb); return
    
    if d=="pts_add":
        ctx.user_data['adm_wait']=('pts_add_uid','آيدي المستخدم')
        await q.edit_message_text("➕ إضافة نقاط\n\n🆔 أرسل آيدي المستخدم:",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","adm_pts")]])); return
    
    if d=="pts_ded":
        ctx.user_data['adm_wait']=('pts_ded_uid','آيدي المستخدم')
        await q.edit_message_text("➖ خصم نقاط\n\n🆔 أرسل آيدي المستخدم:",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","adm_pts")]])); return
    
    if d=="pts_reset":
        ctx.user_data['adm_wait']=('pts_reset_uid','آيدي المستخدم')
        await q.edit_message_text("🔄 تصفير نقاط\n\n⚠️ سيتم تصفير نقاط المستخدم نهائياً!\n\n🆔 أرسل آيدي المستخدم:",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","adm_pts")]])); return
    
    if d=="pts_stats":
        load_all()
        total_users = len(users_data)
        total_pts = sum(u.get('points',0) for u in users_data.values())
        await q.edit_message_text(f"📊 إحصائيات النقاط\n\n👥 إجمالي المستخدمين: {total_users}\n💎 إجمالي النقاط: {total_pts:,}",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_pts")]])); return
    
    if d=="adm_accounts":
        kb = InlineKeyboardMarkup([
            [gbtn("🔍 بحث عن مستخدم","acc_search")],
            [gbtn("👥 عدد المستخدمين","acc_count")],
            [gbtn("📢 رسالة جماعية","acc_broadcast")],
            [redbtn("رجوع","adm_back_main")],
        ])
        await q.edit_message_text("👥 قسم الحسابات\n\nإدارة حسابات المستخدمين:",reply_markup=kb); return
    
    if d=="acc_count":
        load_all()
        await q.answer(f"👥 عدد المستخدمين: {len(users_data)}", show_alert=True); return
    
    if d=="acc_search":
        ctx.user_data['adm_wait']=('acc_search_uid','آيدي المستخدم')
        await q.edit_message_text("🔍 بحث عن مستخدم\n\n🆔 أرسل آيدي المستخدم:",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","adm_accounts")]])); return
    
    if d=="acc_broadcast":
        ctx.user_data['adm_wait']=('broadcast_msg','الرسالة')
        await q.edit_message_text("📢 رسالة جماعية\n\n⚠️ سيتم إرسالها لجميع المستخدمين!\n\n📝 أرسل نص الرسالة:",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","adm_accounts")]])); return
    
    if d=="adm_backup":
        kb = InlineKeyboardMarkup([
            [gbtn("💾 إنشاء نسخة احتياطية","backup_create")],
            [gbtn("♻️ استعادة نسخة","backup_restore")],
            [redbtn("رجوع","adm_back_main")],
        ])
        await q.edit_message_text("💾 النسخ الاحتياطيه\n\nحفظ واستعادة بيانات البوت:",reply_markup=kb); return
    
    if d=="backup_create":
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = f"backups/backup_{ts}"
        os.makedirs(backup_dir, exist_ok=True)
        files = [USER_DATA_FILE, CONFIG_FILE, SERVICES_FILE, SITES_FILE, BTNS_CFG_FILE, CODES_FILE, LINKS_FILE]
        copied = 0
        for f in files:
            if os.path.exists(f):
                shutil.copy2(f, backup_dir)
                copied += 1
        await q.answer(f"✅ تم إنشاء نسخة احتياطية!\n📁 {backup_dir}\n📄 {copied} ملفات", show_alert=True)
        return
    
    if d=="backup_restore":
        ctx.user_data['adm_wait']=('restore_backup','اسم المجلد')
        await q.edit_message_text("♻️ استعادة نسخة\n\n📝 أرسل اسم مجلد النسخة:\n(مثال: backup_20250101_120000)",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","adm_backup")]])); return
    
    if d=="adm_funding":
        await q.edit_message_text("🚀 قسم التمويل\n\n✅ القسم يعمل بشكل طبيعي.",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_back_main")]])); return
    
    if d=="adm_recharge_adm":
        await q.edit_message_text("💳 قسم الشحن\n\n✅ الشحن التلقائي بالنجوم يعمل.\n✅ شحن الوكيل مفعّل.",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_back_main")]])); return
    
    smap={
        'set_bot_name':('bot_name','اسم البوت',False),
        'set_bot_currency':('bot_currency','عملة البوت',False),
        'set_recharge_txt':('recharge_text','كليشه الشحن',False),
        'set_terms_txt':('terms_text','كليشه الشروط',False),
        'set_collect_txt':('collect_text','كليشه التجميع',False),
        'set_funding_txt':('funding_text','كليشه التمويل',False),
        'set_channels_txt':('channels_text','كليشه القنوات',False),
        'set_verify_txt':('verify_text','كليشه الاثباتات',False),
        'set_verify_ch':('verify_channel','قناه الاثباتات',False),
        'set_admin_id':('admin_id','حساب الاداره',True),
        'set_invite_pts':('invite_points','نقاط الرابط',True),
        'set_gift_pts':('gift_points','نقاط الهديه',True),
        'set_coupon_pts':('coupon_points','نقاط الخصم',True),
        'set_transfer_fee':('transfer_fee','عموله التحويل',True),
        'set_channels_list':('channels_list','القنوات',False),
        'set_force_msg':('force_msg','الرساله الاجباريه',False),
    }
    if d in smap:
        k,l,ii=smap[d]; ctx.user_data['adm_wait']=(k,l,ii)
        current_val = str(cfg(k))[:100] if cfg(k) else 'غير معين'
        if k == 'force_msg':
            help_text = """📨 تغيير الرساله الاجباريه

الهاشتاقات المتاحة:
#uytwe = اسم المستخدم
#id = آيدي المستخدم
#qweru = عدد النقاط
#muiip = عدد المستخدمين

مثال:
مرحبا #uytwe
ايديك: #id
نقاطك: #qweru
المستخدمين: #muiip

ارسل الرسالة الجديدة:"""
            await q.edit_message_text(help_text,reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","adm_settings")]]))
        else:
            await q.edit_message_text(f"📝 {l}\n\nالحالي: {current_val}\n\nارسل الجديد:",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","adm_settings")]])); return

async def adm_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!=ADMIN_ID: return
    txt=update.message.text.strip()
    w=ctx.user_data.get('adm_wait')
    
    if w and w[0]=='site_url':
        url=txt.rstrip('/'); ctx.user_data['adm_wait']=('site_key',url); ctx.user_data['site_pending_url']=url
        await update.message.reply_text(f"🔗 تم استلام الرابط: {url}\n\n🔑 ارسل مفتاح API:",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","adm_sites")]])); return
    
    if w and w[0]=='site_key':
        url=ctx.user_data.get('site_pending_url',w[1]); key=txt
        await update.message.reply_text("⏳ جاري التحقق من الموقع...")
        success, result = verify_site(url, key)
        if success:
            from urllib.parse import urlparse; sn=urlparse(url).netloc or url
            load_all(); sites_db[sn]={'url':url,'api_key':key,'balance':result,'active':True}; save_sites()
            ctx.user_data.pop('adm_wait',None); ctx.user_data.pop('site_pending_url',None)
            await update.message.reply_text(f"✅ تم التحقق بنجاح!\n\nاسم الموقع: {sn}\nالرابط: {url}\nالمفتاح: {key[:10]}...\nالرصيد: {result}",reply_markup=get_site_detail_kb(sn))
        else:
            await update.message.reply_text(f"❌ فشل التحقق!\n\nالسبب: {result}\n\n⚠️ تأكد من صحة الرابط والمفتاح",reply_markup=InlineKeyboardMarkup([[redbtn("❌ محاولة أخرى","adm_sites")]]))
            ctx.user_data.pop('adm_wait',None); ctx.user_data.pop('site_pending_url',None)
        return
    
    sa=ctx.user_data.get('adm_svc_add')
    if sa:
        step=sa.get('step','name')
        if step=='name': sa['name']=txt; sa['step']='price'; ctx.user_data['adm_svc_add']=sa; await update.message.reply_text("💰 ارسل السعر (دولار لكل 1000):"); return
        elif step=='price':
            try: sa['price']=int(float(txt)*1000)
            except: await update.message.reply_text("❌ رقم صحيح!"); return
            sa['step']='min'; ctx.user_data['adm_svc_add']=sa; await update.message.reply_text("🔢 الحد الادنى:"); return
        elif step=='min':
            try: sa['min']=int(txt)
            except: await update.message.reply_text("❌ رقم صحيح!"); return
            sa['step']='max'; ctx.user_data['adm_svc_add']=sa; await update.message.reply_text("🔢 الحد الاقصى:"); return
        elif step=='max':
            try: sa['max']=int(txt)
            except: await update.message.reply_text("❌ رقم صحيح!"); return
            load_all(); p=sa['platform']
            ns={'name':sa['name'],'price':sa['price'],'min':sa['min'],'max':sa['max'],'api_id':''}
            if p not in services_db: services_db[p]=[]
            services_db[p].append(ns); save_services(); ctx.user_data.pop('adm_svc_add',None)
            await update.message.reply_text(f"✅ تم حفظ الخدمه!\n\n🏷️ {ns['name']}\n💎 {ns['price']} نقطة\n🔢 {ns['min']}-{ns['max']}",reply_markup=get_platform_svc_kb(p))
            return
    
    if w and w[0]=='edit_name':
        p=w[1]; idx=w[2]
        load_all()
        if p in services_db and idx < len(services_db[p]):
            services_db[p][idx]['name']=txt
            save_services()
        ctx.user_data.pop('adm_wait',None)
        kb, txt_msg = get_service_edit_kb(p, idx)
        await update.message.reply_text("✅ تم تعديل اسم الخدمة",reply_markup=kb)
        return
    
    if w and w[0]=='edit_price':
        p=w[1]; idx=w[2]
        try:
            price=int(txt)
            load_all()
            if p in services_db and idx < len(services_db[p]):
                services_db[p][idx]['price']=price
                save_services()
            ctx.user_data.pop('adm_wait',None)
            kb, txt_msg = get_service_edit_kb(p, idx)
            await update.message.reply_text(f"✅ تم تعديل السعر إلى {price}",reply_markup=kb)
        except:
            await update.message.reply_text("❌ أرسل رقم صحيح!")
        return
    
    if w and w[0]=='edit_min':
        p=w[1]; idx=w[2]
        try:
            min_val=int(txt)
            load_all()
            if p in services_db and idx < len(services_db[p]):
                services_db[p][idx]['min']=min_val
                save_services()
            ctx.user_data.pop('adm_wait',None)
            kb, txt_msg = get_service_edit_kb(p, idx)
            await update.message.reply_text(f"✅ تم تعديل الحد الأدنى إلى {min_val}",reply_markup=kb)
        except:
            await update.message.reply_text("❌ أرسل رقم صحيح!")
        return
    
    if w and w[0]=='edit_max':
        p=w[1]; idx=w[2]
        try:
            max_val=int(txt)
            load_all()
            if p in services_db and idx < len(services_db[p]):
                services_db[p][idx]['max']=max_val
                save_services()
            ctx.user_data.pop('adm_wait',None)
            kb, txt_msg = get_service_edit_kb(p, idx)
            await update.message.reply_text(f"✅ تم تعديل الحد الأقصى إلى {max_val}",reply_markup=kb)
        except:
            await update.message.reply_text("❌ أرسل رقم صحيح!")
        return
    
    if w and w[0]=='make_code_name':
        ctx.user_data['pending_code_name']=txt
        ctx.user_data['adm_wait']=('make_code_pts','عدد النقاط')
        await update.message.reply_text(f"🎟️ الكود: {txt}\n\n💎 أرسل عدد النقاط:")
        return
    
    if w and w[0]=='make_code_pts':
        try:
            pts=int(txt)
            ctx.user_data['pending_code_pts']=pts
            ctx.user_data['adm_wait']=('make_code_max','عدد المستخدمين')
            await update.message.reply_text(f"💎 النقاط: {pts}\n\n👥 أرسل عدد المستخدمين المسموح:")
        except:
            await update.message.reply_text("❌ أرسل رقم صحيح!")
        return
    
    if w and w[0]=='make_code_max':
        try:
            max_uses=int(txt)
            code_name=ctx.user_data.get('pending_code_name','')
            pts=ctx.user_data.get('pending_code_pts',0)
            load_all()
            codes_db[code_name]={'points':pts,'max_uses':max_uses,'used_by':[],'created':datetime.now().isoformat()}
            save_codes()
            ctx.user_data.pop('adm_wait',None)
            ctx.user_data.pop('pending_code_name',None)
            ctx.user_data.pop('pending_code_pts',None)
            await update.message.reply_text(f"✅ تم إنشاء الكود!\n\n🎟️ الكود: {code_name}\n💎 النقاط: {pts}\n👥 الحد الأقصى: {max_uses}",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_gifts")]]))
        except:
            await update.message.reply_text("❌ أرسل رقم صحيح!")
        return
    
    if w and w[0]=='make_link_pts':
        try:
            pts=int(txt)
            ctx.user_data['pending_link_pts']=pts
            ctx.user_data['adm_wait']=('make_link_max','عدد المستخدمين')
            await update.message.reply_text(f"💎 النقاط: {pts}\n\n👥 أرسل عدد المستخدمين المسموح:")
        except:
            await update.message.reply_text("❌ أرسل رقم صحيح!")
        return
    
    if w and w[0]=='make_link_max':
        try:
            max_uses=int(txt)
            pts=ctx.user_data.get('pending_link_pts',0)
            link_id=''.join(random.choices(string.ascii_letters+string.digits,k=8))
            load_all()
            links_db[link_id]={'points':pts,'max_uses':max_uses,'used_by':[],'created':datetime.now().isoformat()}
            save_links()
            ctx.user_data.pop('adm_wait',None)
            ctx.user_data.pop('pending_link_pts',None)
            bot_username=ctx.bot.username or 'Bot'
            full_link=f"https://t.me/{bot_username}?start=link_{link_id}"
            await update.message.reply_text(f"✅ تم إنشاء الرابط!\n\n🔗 {full_link}\n💎 النقاط: {pts}\n👥 الحد الأقصى: {max_uses}",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_gifts")]]))
        except:
            await update.message.reply_text("❌ أرسل رقم صحيح!")
        return
    
    if w and w[0]=='pts_add_uid':
        try:
            tid=int(txt); load_all()
            if str(tid) not in users_data: 
                await update.message.reply_text("❌ المستخدم غير موجود!",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_pts")]]))
                ctx.user_data.pop('adm_wait',None); return
            ctx.user_data['pts_target']=tid
            ctx.user_data['adm_wait']=('pts_add_amt','عدد النقاط')
            await update.message.reply_text(f"👤 المستخدم: {tid}\n\n💎 أرسل عدد النقاط:")
        except: 
            await update.message.reply_text("❌ آيدي رقمي صحيح!",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_pts")]]))
        return
    
    if w and w[0]=='pts_add_amt':
        try:
            amt=int(txt); tid=ctx.user_data.get('pts_target')
            add_pts(tid,amt)
            ctx.user_data.pop('adm_wait',None); ctx.user_data.pop('pts_target',None)
            await update.message.reply_text(f"✅ تم إضافة {amt} نقطة\n💎 الرصيد الحالي: {get_pts(tid)}",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_pts")]]))
        except: 
            await update.message.reply_text("❌ رقم صحيح!",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_pts")]]))
        return
    
    if w and w[0]=='pts_ded_uid':
        try:
            tid=int(txt); load_all()
            if str(tid) not in users_data: 
                await update.message.reply_text("❌ المستخدم غير موجود!",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_pts")]]))
                ctx.user_data.pop('adm_wait',None); return
            ctx.user_data['pts_target']=tid
            ctx.user_data['adm_wait']=('pts_ded_amt','عدد النقاط')
            await update.message.reply_text(f"👤 المستخدم: {tid}\n💎 رصيده: {get_pts(tid)}\n\n➖ أرسل عدد النقاط للخصم:")
        except: 
            await update.message.reply_text("❌ آيدي رقمي صحيح!",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_pts")]]))
        return
    
    if w and w[0]=='pts_ded_amt':
        try:
            amt=int(txt); tid=ctx.user_data.get('pts_target')
            if ded_pts(tid,amt):
                ctx.user_data.pop('adm_wait',None); ctx.user_data.pop('pts_target',None)
                await update.message.reply_text(f"✅ تم خصم {amt} نقطة\n💎 الرصيد الحالي: {get_pts(tid)}",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_pts")]]))
            else:
                await update.message.reply_text(f"❌ رصيد غير كافٍ!\n💎 الرصيد: {get_pts(tid)}",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_pts")]]))
                ctx.user_data.pop('adm_wait',None); ctx.user_data.pop('pts_target',None)
        except: 
            await update.message.reply_text("❌ رقم صحيح!",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_pts")]]))
        return
    
    if w and w[0]=='pts_reset_uid':
        try:
            tid=int(txt); load_all()
            if str(tid) not in users_data: 
                await update.message.reply_text("❌ المستخدم غير موجود!",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_pts")]]))
                ctx.user_data.pop('adm_wait',None); return
            users_data[str(tid)]['points']=0; save_users()
            ctx.user_data.pop('adm_wait',None)
            await update.message.reply_text(f"✅ تم تصفير نقاط المستخدم {tid}",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_pts")]]))
        except: 
            await update.message.reply_text("❌ آيدي رقمي صحيح!",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_pts")]]))
        return
    
    if w and w[0]=='acc_search_uid':
        try:
            tid=int(txt); load_all()
            if str(tid) in users_data:
                u=users_data[str(tid)]
                info=f"👤 معلومات المستخدم\n\n🆔 الآيدي: {tid}\n📛 الاسم: {u.get('first_name','N/A')}\n🔖 اليوزر: @{u.get('username','N/A')}\n💎 النقاط: {u.get('points',0)}\n📦 الطلبات: {len(u.get('orders',[]))}"
                await update.message.reply_text(info,reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_accounts")]]))
            else:
                await update.message.reply_text("❌ المستخدم غير موجود!",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_accounts")]]))
            ctx.user_data.pop('adm_wait',None)
        except: 
            await update.message.reply_text("❌ آيدي رقمي صحيح!",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_accounts")]]))
        return
    
    if w and w[0]=='broadcast_msg':
        msg=txt; load_all()
        sent=0; failed=0
        await update.message.reply_text(f"📢 جاري الإرسال لـ {len(users_data)} مستخدم...")
        for uid in list(users_data.keys()):
            try:
                await ctx.bot.send_message(chat_id=int(uid),text=f"📢 رسالة من الإدارة:\n\n{msg}")
                sent+=1; await asyncio.sleep(0.05)
            except: failed+=1
        ctx.user_data.pop('adm_wait',None)
        await update.message.reply_text(f"✅ اكتمل الإرسال!\n\n✅ تم الإرسال: {sent}\n❌ فشل: {failed}",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_accounts")]]))
        return
    
    if w and w[0]=='exch_add_name':
        ctx.user_data['exch_pending_name']=txt
        ctx.user_data['adm_wait']=('exch_add_cost','تكلفة الفئة')
        await update.message.reply_text(f"📝 الفئة: {txt}\n\n💎 أرسل تكلفة الفئة بالنقاط:")
        return
    
    if w and w[0]=='exch_add_cost':
        try:
            cost=int(txt); name=ctx.user_data.get('exch_pending_name','')
            ctx.user_data.pop('adm_wait',None); ctx.user_data.pop('exch_pending_name',None)
            await update.message.reply_text(f"✅ تم إضافة الفئة!\n\n📝 {name}\n💎 {cost} نقطة",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_exchange")]]))
        except: 
            await update.message.reply_text("❌ رقم صحيح!",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_exchange")]]))
        return
    
    if w and w[0]=='restore_backup':
        backup_path = f"backups/{txt}"
        if os.path.exists(backup_path):
            files = [USER_DATA_FILE, CONFIG_FILE, SERVICES_FILE, SITES_FILE, BTNS_CFG_FILE, CODES_FILE, LINKS_FILE]
            restored = 0
            for f in files:
                src = os.path.join(backup_path, f)
                if os.path.exists(src):
                    shutil.copy2(src, f)
                    restored += 1
            load_all()
            ctx.user_data.pop('adm_wait',None)
            await update.message.reply_text(f"✅ تم الاستعادة!\n📄 {restored} ملفات",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_backup")]]))
        else:
            await update.message.reply_text(f"❌ المجلد غير موجود: {txt}",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","adm_backup")]]))
        return
    
    if w:
        k,l=w[0],w[1]; ii=len(w)>2 and w[2]
        if ii:
            try: v=int(txt); set_cfg(k,v)
            except: await update.message.reply_text("❌ رقم صحيح!",reply_markup=get_settings_kb()); return
        elif k=='channels_list': v=[c.strip() for c in txt.split(',') if c.strip()]; set_cfg(k,v)
        else: v=txt; set_cfg(k,v)
        ctx.user_data.pop('adm_wait',None)
        await update.message.reply_text(f"✅ تم تعديل {l}!\n\nالقيمة: {str(v)[:80]}",reply_markup=get_settings_kb()); return

# ============================================================
#  ██████  البوت الرئيسي  ██████
# ============================================================
async def main_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid=update.effective_user.id; ui=update.effective_user
    txt=update.message.text
    
    if txt.startswith('/start link_'):
        link_id=txt[12:].strip()
        load_all()
        if link_id in links_db:
            link_data=links_db[link_id]
            used_by=link_data.get('used_by',[])
            if str(uid) in used_by:
                await update.message.reply_text("⚠️ لقد استخدمت هذا الرابط مسبقاً!")
            elif len(used_by)>=link_data.get('max_uses',0):
                await update.message.reply_text("❌ انتهى الحد الأقصى لهذا الرابط!")
            else:
                pts=link_data.get('points',0)
                used_by.append(str(uid))
                links_db[link_id]['used_by']=used_by
                save_links()
                add_pts(uid,pts)
                await update.message.reply_text(f"🎉 تم استلام {pts} نقطة!\n\n💎 رصيدك: {get_pts(uid)}")
        else:
            await update.message.reply_text("❌ الرابط غير صالح!")
    
    is_new=initialize_user(uid,ui.first_name,ui.username)
    if is_new: await notify_adm(ctx.bot,ui,len(users_data))
    
    force_msg = cfg('force_msg', '')
    if force_msg:
        processed_msg = process_force_msg(force_msg, uid, ui.first_name, get_pts(uid), len(users_data))
        if processed_msg:
            await update.message.reply_text(processed_msg, reply_markup=get_main_keyboard())
            return
    
    await update.message.reply_text(WELCOME.format(name=ui.first_name or 'كروري',user_id=uid,points=get_pts(uid)),reply_markup=get_main_keyboard())

async def main_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer()
    uid=q.from_user.id; d=q.data; initialize_user(uid)

    if d=="services":
        await q.edit_message_text(SVC_TEXT,reply_markup=get_services_keyboard()); return

    if d.startswith("svc_") and not d.startswith("svc_order_") and not d.startswith("user_svc_page_"):
        plat=d.replace("svc_",""); load_all()
        svcs=services_db.get(plat,[])
        if not svcs:
            await q.edit_message_text(f"📱 {plat}\n\n⚠️ لا توجد خدمات متاحة حالياً.",
                reply_markup=InlineKeyboardMarkup([[sbtn("رجوع","services","back",s="danger")]])); return
        ctx.user_data[f'user_svc_page_{plat}'] = 0
        await q.edit_message_text(f"📱 {plat}\n\nاختر الخدمة 👇",reply_markup=get_user_services_kb(plat, 0)); return
    
    if d.startswith("user_svc_page_"):
        parts = d.split("_")
        plat = parts[3]
        page = int(parts[4])
        ctx.user_data[f'user_svc_page_{plat}'] = page
        await q.edit_message_reply_markup(reply_markup=get_user_services_kb(plat, page))
        return

    if d.startswith("svc_order_"):
        parts=d.split("_"); plat=parts[2]; idx=int(parts[3]); load_all()
        svcs=services_db.get(plat,[])
        if idx>=len(svcs): await q.answer("❌ خدمة غير موجودة",show_alert=True); return
        s=svcs[idx]
        ctx.user_data['pending_order']={'platform':plat,'idx':idx,'step':'qty'}
        await q.edit_message_text(
            f"(🏷️) اسم الخدمة : {s['name']}\n\n(💎) السعر : {s['price']} نقطة لكل 1000\n(🆔) ايدي الخدمة : {s.get('api_id','N/A')}\n(🔢) الحد الأدنى: {s.get('min',1)} | الأقصى: {s.get('max',10000)}\n\n(📥) ارسل الكمية التي تريد طلبها الان :",
            reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","services")]]))
        return

    fd={"fund_channel_group":"🚀 تمويل قناتك او كروبك","my_current_fundings":"📋 تمويلاتي الجارية","collect_points_funding":"➕ تجميع نقاط"}
    if d=="funding_section": await q.edit_message_text(cfg('funding_text') or FUND_WELC,reply_markup=get_funding_kb()); return
    if d in fd: await q.edit_message_text(f"{fd[d]}\n\n⚠️ قيد التطوير...",reply_markup=InlineKeyboardMarkup([[fbtn("رجوع","funding_section","fund_back",s="danger")]])); return
    if d=="recharge_points": await q.edit_message_text(get_rech_txt(),reply_markup=get_recharge_kb()); return
    if d=="collect_points": await q.edit_message_text(cfg('collect_text') or COLL_TXT,reply_markup=get_collect_kb()); return
    if d=="daily_gift":
        load_all(); today=date.today().isoformat(); gp=int(cfg('gift_points',50))
        if users_data.get(str(uid),{}).get('last_daily')==today:
            await q.edit_message_text("🎁 الهدية اليومية\n\n❌ استلمت هديتك اليوم!\n⏰ عاود غداً.",reply_markup=InlineKeyboardMarkup([[cbtn("⟨ رجوع ","collect_points","collect_back",s="danger")]])); return
        add_pts(uid,gp); users_data[str(uid)]['last_daily']=today; users_data[str(uid)]['daily_count']=users_data[str(uid)].get('daily_count',0)+1; save_users()
        await q.edit_message_text(f"🎁 الهدية اليومية\n\n✅ تم استلام {gp} نقطة!\n💎 رصيدك: {get_pts(uid)}",reply_markup=InlineKeyboardMarkup([[cbtn("⟨ رجوع ","collect_points","collect_back",s="danger")]])); return
    if d=="invite_link":
        bn=ctx.bot.username or 'Bot'; iu=f"https://t.me/{bn}?start={uid}"
        su=f"https://t.me/share/url?url={iu}&text=سجل ببوت رشق ستار واحصل على نقاط مجانية!"
        await q.edit_message_text(f"🔗 رابط الدعوة\n\n📎 `{iu}`\n\n💰 {cfg('invite_points',200)} نقطة لكل دعوة!\n📊 دعواتك: {len(users_data.get(str(uid),{}).get('referrals',[]))}",
            reply_markup=InlineKeyboardMarkup([[cbtn("⟨ مشاركة الرابط ","x",url=su,s="success")],[cbtn("⟨ رجوع ","collect_points","collect_back",s="danger")]])); return
    if d=="subscribe_channels": await q.edit_message_text("📺 الاشتراك بالقنوات\n\n⚠️ قيد التطوير...",reply_markup=InlineKeyboardMarkup([[cbtn("⟨ رجوع ","collect_points","collect_back",s="danger")]])); return
    if d=="weekly_contest": await q.edit_message_text("🏆 المسابقة الأسبوعية\n\n⚠️ قيد التطوير...",reply_markup=InlineKeyboardMarkup([[cbtn("⟨ رجوع ","collect_points","collect_back",s="danger")]])); return
    if d=="check_order":
        await q.edit_message_text("🔍 أرسل رقم الطلب لفحصه:",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]]))
        ctx.user_data['awaiting_order_check']=True; return
    if d=="my_orders":
        load_all(); ords=users_data.get(str(uid),{}).get('orders',[]); tot=len(ords)
        if tot==0: await q.edit_message_text("📋 جميع طلباتك\n\nلا يوجد لديك طلبات حالياً",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]])); return
        pg=ctx.user_data.get('orders_page',1); pp=1; tp=max(1,(tot+pp-1)//pp); pg=min(pg,tp)
        si=(pg-1)*pp; co=ords[si]; oid=co.get('order_id','N/A'); done=co.get('status')=='مكتمل'
        sb=obtn("✅ تم اكمال بنجاح",f"order_detail_{si}","order_done") if done else obtn("⏳ في الانتظار ⚡",f"order_detail_{si}","order_waiting")
        await q.edit_message_text(f"🌟 جميع طلباتك\n\n🌟 إجمالي: {tot}\n📄 عرض: {si+1}-{min(si+pp,tot)} من {tot}",
            reply_markup=InlineKeyboardMarkup([[sb,obtn(f"{oid} 🙂",f"order_detail_{si}","order_id_btn")],[obtn(f"📄 {pg}/{tp} ✨%","orders_page_next","order_page")],[obtn("رجوع","back","orders_back")]])); return
    if d.startswith("order_detail_"):
        idx=int(d.split("_")[2]); load_all(); ords=users_data.get(str(uid),{}).get('orders',[])
        if idx<len(ords): await q.edit_message_text(fmt_ord(ords[idx]),reply_markup=InlineKeyboardMarkup([[obtn("رجوع","my_orders","orders_back")]])); return
    if d=="orders_page_next":
        load_all(); ords=users_data.get(str(uid),{}).get('orders',[]); tot=len(ords); pp=1
        tp=max(1,(tot+pp-1)//pp); np=(ctx.user_data.get('orders_page',1)%tp)+1; ctx.user_data['orders_page']=np
        si=(np-1)*pp; co=ords[si]; oid=co.get('order_id','N/A'); done=co.get('status')=='مكتمل'
        sb=obtn("✅ تم اكمال بنجاح",f"order_detail_{si}","order_done") if done else obtn("⏳ في الانتظار ⚡",f"order_detail_{si}","order_waiting")
        await q.edit_message_text(f"🌟 جميع طلباتك\n\n🌟 إجمالي: {tot}\n📄 عرض: {si+1}-{min(si+pp,tot)} من {tot}",
            reply_markup=InlineKeyboardMarkup([[sb,obtn(f"{oid} 🙂",f"order_detail_{si}","order_id_btn")],[obtn(f"📄 {np}/{tp} ✨%","orders_page_next","order_page")],[obtn("رجوع","back","orders_back")]])); return
    if d=="use_code":
        await q.edit_message_text("⌁︙ ارسل الكود",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]]))
        ctx.user_data['awaiting_code']=True; return
    if d=="transfer_points":
        await q.edit_message_text("📤 تحويل النقاط\n\n🆔 أرسل آيدي المستخدم:",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]]))
        ctx.user_data['awaiting_transfer_user']=True; return
    if d=="orders_done": await q.answer(url="https://t.me/qwe41h"); return
    if d=="terms_use": await q.edit_message_text(get_terms_txt(),reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]])); return
    if d=="account":
        load_all(); u=users_data.get(str(uid),{})
        await q.edit_message_text(f"👤 | معلومات حسابك\n🆔 | ايدي حسابك : {uid}\n💎 | عدد نقاطك : {u.get('points',0)}\n📨 | عدد الدعوات : {len(u.get('referrals',[]))}\n📦 | عدد طلباتك : {len(u.get('orders',[]))}\n\n💙 | شكرا لاستخدامك بوت رشق ستار",
            reply_markup=InlineKeyboardMarkup([[redbtn("رجوع ➡","back")]])); return
    if d=="exchange_points": await q.edit_message_text(EXCH_TXT,reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]])); return
    if d=="back":
        nm=users_data.get(str(uid),{}).get('first_name','كروري')
        await q.edit_message_text(WELCOME.format(name=nm,user_id=uid,points=get_pts(uid)),reply_markup=get_main_keyboard()); return

# ============================================================
#  ██████  معالجة الأزرار الخاصة - إصلاح نهائي للزرين ✅
# ============================================================
async def special_buttons_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """معالج خاص للأزرار: confirm_order, cancel_order, confirm_fetch_"""
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    d = q.data
    
    # ✅ زر إلغاء الطلب
    if d == "cancel_order":
        ctx.user_data.pop('pending_order', None)
        await q.edit_message_text("❌ تم إلغاء الطلب.", reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]]))
        return
    
    # ✅ زر موافقة الطلب - الإصلاح النهائي
    if d == "confirm_order":
        po = ctx.user_data.get('pending_order')
        if not po:
            await q.answer("❌ لا يوجد طلب", show_alert=True)
            return
        
        load_all()
        plat = po['platform']
        idx = po['idx']
        
        if plat not in services_db or idx >= len(services_db[plat]):
            await q.answer("❌ الخدمة غير موجودة", show_alert=True)
            ctx.user_data.pop('pending_order', None)
            return
            
        s = services_db[plat][idx]
        cost = po['cost']
        
        if not ded_pts(uid, cost):
            await q.edit_message_text(f"❌ نقاطك غير كافيه\n\n💰 المطلوب: {cost} نقطة\n💎 رصيدك: {get_pts(uid)} نقطة\n\nتواصل مع الدعم @wewv4",
                reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]]))
            ctx.user_data.pop('pending_order', None)
            return
        
        oid = f"#{random.randint(10000,99999)}"
        order = {
            'order_id': oid,
            'service': s['name'],
            'platform': plat,
            'link': po['link'],
            'quantity': po['qty'],
            'completed': 0,
            'price': cost,
            'status': 'قيد التنفيذ',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'api_id': s.get('api_id', '')
        }
        users_data[str(uid)].setdefault('orders', []).append(order)
        save_users()
        ctx.user_data.pop('pending_order', None)
        
        username = users_data[str(uid)].get('username', '')
        await send_order_to_channel(ctx.bot, order, uid, username)
        
        await q.edit_message_text(
            f"✅ تم استلام طلبك بنجاح!\n"
            f"📱 المنصة: {plat}\n"
            f"🔢 الكمية: {po['qty']}\n"
            f"💰 التكلفة: {cost} نقطة\n"
            f"💎 نقاطك الحالية: {get_pts(uid)} نقطة\n"
            f"🆔 رقم الطلب: {oid}\n"
            f"😌 لمعرفة حالة طلبك استخدم زر فحص الطلب",
            reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]])
        )
        
        try:
            await ctx.bot.send_message(chat_id=ADMIN_ID, text=f"📦 طلب جديد!\n👤 {uid}\n🏷️ {s['name']}\n📱 {plat}\n🔢 {po['qty']}\n💰 {cost} نقطة\n🆔 {oid}")
        except:
            pass
        return
    
    # ✅ زر استرداد المحدد - الإصلاح النهائي
    if d.startswith("confirm_fetch_"):
        p = d[12:]
        selected = ctx.user_data.get(f'fetch_selected_{p}', set())
        services_list = ctx.user_data.get(f'fetch_services_{p}', [])
        
        if not selected:
            await q.answer("❌ لم تحدد أي خدمة!", show_alert=True)
            return
        
        if not services_list:
            await q.answer("❌ لا توجد خدمات للاسترداد", show_alert=True)
            return
        
        load_all()
        fetched = []
        for idx in sorted(selected):
            if idx < len(services_list):
                s = services_list[idx]
                fetched.append({
                    'name': s.get('name', 'خدمة'),
                    'price': int(float(s.get('rate', s.get('price', 0))) * 1000),
                    'min': int(s.get('min', 1)),
                    'max': int(s.get('max', 10000)),
                    'api_id': s.get('service', s.get('id', ''))
                })
        
        if fetched:
            if p not in services_db:
                services_db[p] = []
            services_db[p] = fetched
            save_services()
            
            ctx.user_data.pop(f'fetch_services_{p}', None)
            ctx.user_data.pop(f'fetch_selected_{p}', None)
            ctx.user_data.pop(f'fetch_page_{p}', None)
            
            await q.edit_message_text(
                f"✅ تم استرداد {len(fetched)} خدمة لـ {p} بنجاح!\n\n"
                f"📊 الخدمات المضافة: {len(fetched)}\n"
                f"📱 المنصة: {p}",
                reply_markup=InlineKeyboardMarkup([[redbtn("رجوع", f"adm_plat_{p}")]])
            )
        else:
            await q.answer("❌ فشل استرداد الخدمات", show_alert=True)
        return

# ============================================================
#  ██████  معالجة الرسائل النصية ✅
# ============================================================
async def main_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid=update.effective_user.id; txt=update.message.text.strip()

    if uid==ADMIN_ID:
        if ctx.user_data.get('adm_wait') or ctx.user_data.get('adm_svc_add') or ctx.user_data.get('site_pending_url'):
            await adm_msg(update,ctx); return
        if ctx.user_data.get('eb_wait_rename') or ctx.user_data.get('eb_wait_emoji'):
            await eb_msg(update,ctx); return

    po=ctx.user_data.get('pending_order')
    if po and po.get('step')=='qty':
        try:
            qty=int(txt); load_all(); plat=po['platform']; idx=po['idx']; s=services_db[plat][idx]
            if qty<s.get('min',1) or qty>s.get('max',10000):
                await update.message.reply_text(f"❌ الكمية يجب بين {s.get('min',1)} و {s.get('max',10000)}"); return
            cost=max(1,int(s['price']*qty/1000))
            po['qty']=qty; po['cost']=cost; po['step']='link'; ctx.user_data['pending_order']=po
            await update.message.reply_text(f"🔢 الكمية: {qty}\n💰 التكلفة: {cost} نقطة\n\n🔗 ارسل رابط الطلب حسب طلبك :")
        except ValueError: await update.message.reply_text("❌ ارسل رقم صحيح!")
        return

    if po and po.get('step')=='link':
        load_all(); plat=po['platform']; idx=po['idx']; s=services_db[plat][idx]
        po['link']=txt; po['step']='confirm'; ctx.user_data['pending_order']=po
        await update.message.reply_text(
            f"📋 تأكيد الطلب\n\n🏷️ الخدمة: {s['name']}\n📱 المنصة: {plat}\n🔗 الرابط: {txt}\n🔢 الكمية: {po['qty']}\n💰 التكلفة: {po['cost']} نقطة\n\n⚠️ تأكد من صحة الرابط قبل التأكيد\nهل تريد تأكيد هذا الطلب؟",
            reply_markup=InlineKeyboardMarkup([
                [rbtn("✅ تأكيد الطلب","confirm_order",s="success")],
                [redbtn("❌ الغاء الطلب","cancel_order")],
            ]))
        return

    if ctx.user_data.get('awaiting_order_check'):
        load_all(); found=None
        for u in users_data.values():
            for o in u.get('orders',[]):
                if o.get('order_id')==txt: found=o; break
            if found: break
        if found: await update.message.reply_text(f"🔍 نتيجة الفحص\n\n{fmt_ord(found)}",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]]))
        else: await update.message.reply_text("❌ لم يتم العثور على طلب بهذا الرقم.",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]]))
        ctx.user_data['awaiting_order_check']=False; return

    if ctx.user_data.get('awaiting_code'):
        code=txt.upper(); cp=int(cfg('coupon_points',75))
        codes={'WELCOME':100,'BONUS':50,'VIP':200,'STAR':150,'FREE':cp}
        load_all(); used=users_data.get(str(uid),{}).get('used_codes',[])
        if code in used: await update.message.reply_text("⚠️ تم استخدامه مسبقاً!",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]]))
        elif code in codes:
            p=codes[code]; add_pts(uid,p); users_data[str(uid)].setdefault('used_codes',[]).append(code); save_users()
            await update.message.reply_text(f"✅ تم استلام النقاط : {p} 💎\n\n📊 رصيدك: {get_pts(uid)} نقطة",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]]))
        elif code in codes_db:
            code_data=codes_db[code]
            used_by=code_data.get('used_by',[])
            if len(used_by)>=code_data.get('max_uses',0):
                await update.message.reply_text("❌ انتهى الحد الأقصى لهذا الكود!",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]]))
            else:
                p=code_data.get('points',0)
                used_by.append(str(uid))
                codes_db[code]['used_by']=used_by
                save_codes()
                add_pts(uid,p)
                users_data[str(uid)].setdefault('used_codes',[]).append(code)
                save_users()
                await update.message.reply_text(f"✅ تم استلام النقاط : {p} 💎\n\n📊 رصيدك: {get_pts(uid)} نقطة",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]]))
        else: await update.message.reply_text("❌ الكود غير صالح أو غير موجود.",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]]))
        ctx.user_data['awaiting_code']=False; return

    if ctx.user_data.get('awaiting_transfer_user'):
        try:
            tid=int(txt); load_all()
            if str(tid) not in users_data: await update.message.reply_text("❌ المستخدم غير موجود!",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]])); ctx.user_data['awaiting_transfer_user']=False; return
            ctx.user_data['transfer_target']=tid; ctx.user_data['awaiting_transfer_amount']=True; ctx.user_data['awaiting_transfer_user']=False
            await update.message.reply_text(f"👤 اريد الشخص : {tid}\n\n📤 ارسل عدد النقاط:")
        except ValueError: await update.message.reply_text("❌ آيدي رقمي صحيح!",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]]))
        return
    if ctx.user_data.get('awaiting_transfer_amount'):
        try:
            amt=int(txt); tid=ctx.user_data.get('transfer_target')
            if amt<=0: await update.message.reply_text("❌ المبلغ اكبر من 0"); return
            if not ded_pts(uid,amt): await update.message.reply_text(f"❌ رصيدك غير كافي!\n💰 المطلوب: {amt}\n💎 رصيدك: {get_pts(uid)}",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]])); ctx.user_data['awaiting_transfer_amount']=False; return
            add_pts(tid,amt); load_all()
            users_data[str(uid)]['points_sent']=users_data[str(uid)].get('points_sent',0)+amt
            users_data[str(tid)]['points_received']=users_data[str(tid)].get('points_received',0)+amt; save_users()
            await update.message.reply_text(f"✅ تم التحويل بنجاح\n\n👤 اللي حولت له : {tid}\n💎 النقاط : {amt}\n\n📊 رصيدك: {get_pts(uid)}",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]]))
            try: await ctx.bot.send_message(chat_id=tid,text=f"🎉 تم استلام {amt} نقطة من {uid}\n💎 رصيدك: {get_pts(tid)}")
            except: pass
        except ValueError: await update.message.reply_text("❌ عدد صحيح!",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","back")]]))
        ctx.user_data['awaiting_transfer_amount']=False; ctx.user_data['transfer_target']=None; return

    if txt.startswith('/start ') and len(txt)>7:
        rid=txt[7:].strip()
        if rid.isdigit() and rid!=str(uid):
            load_all()
            if str(rid) in users_data:
                refs=users_data[str(rid)].get('referrals',[])
                if str(uid) not in refs:
                    refs.append(str(uid)); users_data[str(rid)]['referrals']=refs
                    ip=int(cfg('invite_points',200)); add_pts(int(rid),ip); save_users()
                    try: await ctx.bot.send_message(chat_id=int(rid),text=f"🎉 شخص جديد عبر رابطك!\n💎 +{ip} نقطة\n📊 رصيدك: {get_pts(int(rid))}")
                    except: pass
        return

# ============================================================
#  ██████  بوت الشحن التلقائي  ██████
# ============================================================
async def auto_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid=update.effective_user.id; ui=update.effective_user
    is_new=initialize_user(uid,ui.first_name,ui.username)
    if is_new: await notify_adm(ctx.bot,ui,len(users_data))
    await update.message.reply_text(AUTO_WELC.format(user_id=uid,points=get_pts(uid)),reply_markup=get_auto_kb())

async def auto_cb(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); uid=q.from_user.id; d=q.data; initialize_user(uid)
    if d=="auto_back": await q.edit_message_text(AUTO_WELC.format(user_id=uid,points=get_pts(uid)),reply_markup=get_auto_kb()); return
    if d=="auto_recharge": await q.edit_message_text(PAY_METH,reply_markup=get_pay_method_kb()); return
    if d=="pay_stars": await q.edit_message_text(STARS_CH,reply_markup=get_stars_kb()); return
    if d=="pay_asiacell": await q.edit_message_text("📱 اسياسيل\n\nلم يتم تفعيل حتى الان انتظر . . .\n\n@wewv4",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","auto_back")]])); return
    if d=="pay_crypto": await q.edit_message_text("🪙 العمله الرقميه\n\nيحدث الان عندنا مشكله .\n\n@wewv4",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","auto_back")]])); return
    if d.startswith("stars_") and d!="stars_custom":
        stars=int(d.split("_")[1]); pts=stars*100
        await q.edit_message_text(f"⭐ تفاصيل الشحن\n\n🌟 النجوم: {stars}\n✨ النقاط: {pts:,}",reply_markup=get_pay_confirm_kb(stars)); return
    if d=="stars_custom":
        await q.edit_message_text("🔢 أرسل عدد النجوم:",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","auto_back")]]))
        ctx.user_data['awaiting_custom_stars']=True; return
    if d=="coupon_discount": await q.edit_message_text("🎟️ كوبون الخصم\n\n⚠️ لا توجد كوبونات حالياً.\n\n@wewv4",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","auto_back")]])); return
    if d.startswith("do_pay_"):
        stars=int(d.split("_")[2]); pts=stars*100
        try:
            await ctx.bot.send_invoice(chat_id=uid,title=f"شحن {pts:,} نقطة",
                description=f"⭐ {stars} نجمة = {pts:,} نقطة\nسيتم إضافة النقاط فوراً ✅",
                payload=f"stars_{stars}_{uid}",provider_token="",currency="XTR",
                prices=[LabeledPrice(label=f"{stars} نجمة ⭐",amount=stars)])
        except Exception as e:
            logger.error(f"Stars: {e}")
            await q.edit_message_text("❌ خطأ بالدفع\n\n@wewv4",reply_markup=InlineKeyboardMarkup([[redbtn("رجوع","auto_back")]]))
        return
    if d=="prices": await q.edit_message_text(get_auto_prices(),reply_markup=InlineKeyboardMarkup([[rbtn("⚡ شحن النقاط","auto_recharge",s="success")],[redbtn("❌ رجوع","auto_back")]])); return
    if d=="offers": await q.edit_message_text(AUTO_OFF,reply_markup=InlineKeyboardMarkup([[rbtn("⚡ شحن النقاط","auto_recharge",s="success")],[redbtn("❌ رجوع","auto_back")]])); return
    if d=="agent_recharge": await q.answer(url="https://t.me/wewv4"); return
    if d=="my_account":
        load_all(); u=users_data.get(str(uid),{})
        await q.edit_message_text(f"🤭 • معلومات حسابك\n\n☑️ • معرف الحساب: {uid}\n💎 • إجمالي النقاط المشحونة: {u.get('total_charged',0)} نقطة\n⭐ • إجمالي النجوم المدفوعه: {u.get('total_stars_paid',0)}\n💷 • اجمالي رصيد اسياسيل المدفوع : {u.get('total_asiacell_paid',0)} د.ع",reply_markup=InlineKeyboardMarkup([[redbtn("❌ رجوع","auto_back")]])); return
    if d=="transactions":
        load_all(); txs=users_data.get(str(uid),{}).get('transactions',[])
        if not txs: await q.edit_message_text("📋 آخر معاملاتك\n\nلا توجد معاملات بعد.",reply_markup=InlineKeyboardMarkup([[redbtn("❌ رجوع","auto_back")]])); return
        t="📋 آخر معاملاتك\n\n"
        for tx in txs[-5:][::-1]: t+=f"🔹 {tx['type']} | {tx['amount']} | {tx['points']:,} نقطة | {tx['status']} | {tx['date']}\n"
        await q.edit_message_text(t,reply_markup=InlineKeyboardMarkup([[redbtn("❌ رجوع","auto_back")]])); return

async def auto_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if ctx.user_data.get('awaiting_custom_stars'):
        try:
            stars=int(update.message.text.strip()); pts=stars*100; ctx.user_data['awaiting_custom_stars']=False
            await update.message.reply_text(f"⭐ تفاصيل الشحن\n\n🌟 النجوم: {stars}\n✨ النقاط: {pts:,}",reply_markup=get_pay_confirm_kb(stars))
        except: await update.message.reply_text("❌ رقم صحيح!",reply_markup=InlineKeyboardMarkup([[redbtn("❌ إلغاء","auto_back")]])); ctx.user_data['awaiting_custom_stars']=False

async def pre_checkout(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def successful_payment(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid=update.effective_user.id; pay=update.message.successful_payment; pl=pay.invoice_payload
    try: parts=pl.split("_"); stars=int(parts[1]); pts=stars*100
    except: stars=pay.total_amount; pts=stars*100
    add_pts(uid,pts); add_tx(uid,'نجوم',stars,pts,'مكتمل')
    try: await ctx.bot.send_message(chat_id=ADMIN_ID,text=f"⭐ شحن جديد!\n👤 {uid}\n⭐ {stars} نجمة\n💎 {pts:,} نقطة\n🆔 {pay.telegram_payment_charge_id}")
    except: pass
    await update.message.reply_text(f"✅ تم الدفع بنجاح!\n\n⭐ النجوم: {stars}\n💎 النقاط: {pts:,}\n\n📊 رصيدك: {get_pts(uid):,} نقطة",reply_markup=get_auto_kb())

# ============================================================
#  ██████  التشغيل - الترتيب الصحيح للـ handlers ✅
# ============================================================
async def run_both():
    load_all()
    
    # تصفير الخدمات
    for p in PLATFORMS:
        services_db[p] = []
    save_services()
    
    print("="*55)
    print("🚀 بوت رشق ستار  +  ⚡ بوت الشحن التلقائي")
    print("🛠️  /admin  |  /eb")
    print("👑 المسؤول: 8010837412")
    print("✅ إصلاح نهائي: زر موافقة الطلب")
    print("✅ إصلاح نهائي: زر استرداد المحدد")
    print("="*55)

    ma = Application.builder().token(MAIN_BOT_TOKEN).build()
    ma.add_handler(CommandHandler("start", main_start))
    ma.add_handler(CommandHandler("admin", adm_cmd))
    ma.add_handler(CommandHandler("eb", eb_cmd))
    ma.add_handler(CallbackQueryHandler(eb_cb, pattern=r"^eb_"))
    
    # ✅ الحل النهائي: handler خاص للأزرار المشكلة - BEFORE main_cb
    ma.add_handler(CallbackQueryHandler(special_buttons_handler, pattern=r"^(confirm_order|cancel_order|confirm_fetch_.*)$"))
    
    # adm_cb لباقي أزرار الأدمن
    ma.add_handler(CallbackQueryHandler(adm_cb, pattern=r"^adm_|^set_|^site_|^toggle_|^edit_svc_|^fetch_page_|^select_all_|^deselect_all_|^toggle_select_|^exch_|^pts_|^acc_|^backup_|^make_"))
    
    # main_cb للأزرار العادية - LAST callback handler
    ma.add_handler(CallbackQueryHandler(main_cb))
    
    # main_msg للرسائل النصية
    ma.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, main_msg))

    aa = Application.builder().token(AUTO_BOT_TOKEN).build()
    aa.add_handler(CommandHandler("start", auto_start))
    aa.add_handler(CallbackQueryHandler(auto_cb))
    aa.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_msg))
    aa.add_handler(PreCheckoutQueryHandler(pre_checkout))
    aa.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

    async with ma, aa:
        await ma.start()
        await aa.start()
        await ma.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        await aa.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        print("✅ البوت الرئيسي يعمل...")
        print("✅ بوت الشحن التلقائي يعمل...")
        ev = asyncio.Event()
        try:
            await ev.wait()
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            await ma.updater.stop()
            await aa.updater.stop()
            await ma.stop()
            await aa.stop()
            print("🛑 تم الإيقاف.")

def main():
    try:
        asyncio.run(run_both())
    except KeyboardInterrupt:
        print("\n🛑 تم الإيقاف.")

if __name__ == '__main__':
    main()