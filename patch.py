import os
P="com.yks27.app"
d="android/app/src/main/java/com/yks27/app/"
r="android/app/src/main/res/"
for x in (d,r+"layout",r+"drawable",r+"xml"):os.makedirs(x,exist_ok=True)
H="package "+P+";\n"
J={}
J["MainActivity"]=H+"""import android.os.Bundle;
import com.getcapacitor.BridgeActivity;
public class MainActivity extends BridgeActivity {
  @Override public void onCreate(Bundle b){ registerPlugin(StopwatchPlugin.class); super.onCreate(b); }
}"""
J["StopwatchPlugin"]=H+"""import com.getcapacitor.*;
import com.getcapacitor.annotation.CapacitorPlugin;
@CapacitorPlugin(name = "Stopwatch")
public class StopwatchPlugin extends Plugin {
  private void done(PluginCall c){ long[] s = Sw.state(getContext()); JSObject o = new JSObject(); o.put("acc", s[0]); o.put("start", s[1]); c.resolve(o); }
  @PluginMethod public void getState(PluginCall c){ done(c); }
  @PluginMethod public void toggle(PluginCall c){ Sw.toggle(getContext()); done(c); }
  @PluginMethod public void reset(PluginCall c){ Sw.reset(getContext()); Sw.hide(getContext()); done(c); }
  @PluginMethod public void setDates(PluginCall c){
    Sw.p(getContext()).edit().putString("tyt", c.getString("tyt","2027-06-19T10:15")).putString("ayt", c.getString("ayt","2027-06-20T10:15")).apply();
    DaysWidget.refresh(getContext()); c.resolve();
  }
}"""
J["SwReceiver"]=H+"""import android.content.*;
public class SwReceiver extends BroadcastReceiver {
  @Override public void onReceive(Context c, Intent i){
    if ("R".equals(i.getAction())) { Sw.reset(c); Sw.show(c); } else Sw.toggle(c);
  }
}"""
J["Sw"]=H+"""import android.app.*;
import android.content.*;
import android.os.Build;
public class Sw {
  static SharedPreferences p(Context c){ return c.getSharedPreferences("sw", 0); }
  public static long[] state(Context c){ SharedPreferences p = p(c); return new long[]{ p.getLong("acc",0), p.getLong("start",0) }; }
  static String fmt(long ms){ long t = ms/1000; return (t/3600) + ":" + String.format("%02d:%02d", t%3600/60, t%60); }
  public static void toggle(Context c){
    long[] s = state(c); long n = System.currentTimeMillis();
    if (s[1] > 0) p(c).edit().putLong("acc", s[0] + n - s[1]).putLong("start", 0).apply(); else p(c).edit().putLong("start", n).apply();
    show(c);
  }
  public static void reset(Context c){ p(c).edit().putLong("acc",0).putLong("start",0).apply(); }
  public static void hide(Context c){ ((NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE)).cancel(7); }
  public static void show(Context c){
    NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE);
    if (Build.VERSION.SDK_INT >= 26) nm.createNotificationChannel(new NotificationChannel("sw", "Kronometre", NotificationManager.IMPORTANCE_LOW));
    long[] s = state(c); boolean run = s[1] > 0; int fl = PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE;
    PendingIntent tg = PendingIntent.getBroadcast(c, 1, new Intent(c, SwReceiver.class).setAction("T"), fl);
    PendingIntent rs = PendingIntent.getBroadcast(c, 2, new Intent(c, SwReceiver.class).setAction("R"), fl);
    PendingIntent open = PendingIntent.getActivity(c, 3, new Intent(c, MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP), fl);
    Notification.Builder b = Build.VERSION.SDK_INT >= 26 ? new Notification.Builder(c, "sw") : new Notification.Builder(c);
    b.setSmallIcon(android.R.drawable.ic_menu_recent_history).setContentTitle("Çalışma kronometresi").setOngoing(true).setOnlyAlertOnce(true).setContentIntent(open)
     .addAction(0, run ? "Durdur" : "Başlat", tg).addAction(0, "Sıfırla", rs);
    if (run) b.setContentText("Çalışıyor").setUsesChronometer(true).setShowWhen(true).setWhen(s[1] - s[0]);
    else b.setContentText("Durdu: " + fmt(s[0])).setShowWhen(false);
    nm.notify(7, b.build());
  }
}"""
J["DaysWidget"]=H+"""import android.app.PendingIntent;
import android.appwidget.*;
import android.content.*;
import android.widget.RemoteViews;
import java.text.SimpleDateFormat;
import java.util.Locale;
public abstract class DaysWidget extends AppWidgetProvider {
  abstract String kind();
  static long target(Context c, String k){
    String d = Sw.p(c).getString(k, k.equals("tyt") ? "2027-06-19T10:15" : "2027-06-20T10:15");
    try { return new SimpleDateFormat("yyyy-MM-dd'T'HH:mm", Locale.US).parse(d).getTime(); } catch (Exception e) { return 0; }
  }
  static RemoteViews views(Context c, String k){
    long ms = target(c, k) - System.currentTimeMillis(); long days = ms <= 0 ? 0 : (ms + 86399999L) / 86400000L;
    RemoteViews v = new RemoteViews(c.getPackageName(), R.layout.yks_widget);
    v.setTextViewText(R.id.w_name, k.toUpperCase(Locale.US)); v.setTextViewText(R.id.w_days, String.valueOf(days));
    v.setOnClickPendingIntent(R.id.w_root, PendingIntent.getActivity(c, 4, new Intent(c, MainActivity.class), PendingIntent.FLAG_IMMUTABLE));
    return v;
  }
  static void refresh(Context c){
    AppWidgetManager m = AppWidgetManager.getInstance(c);
    for (int id : m.getAppWidgetIds(new ComponentName(c, TytWidget.class))) m.updateAppWidget(id, views(c, "tyt"));
    for (int id : m.getAppWidgetIds(new ComponentName(c, AytWidget.class))) m.updateAppWidget(id, views(c, "ayt"));
  }
  @Override public void onUpdate(Context c, AppWidgetManager m, int[] ids){ refresh(c); }
  @Override public void onReceive(Context c, Intent i){ super.onReceive(c, i); refresh(c); }
}"""
J["TytWidget"]=H+"public class TytWidget extends DaysWidget { String kind(){ return \"tyt\"; } }"
J["AytWidget"]=H+"public class AytWidget extends DaysWidget { String kind(){ return \"ayt\"; } }"
for n,t in J.items(): open(d+n+".java","w",encoding="utf-8").write(t)
A='xmlns:android="http://schemas.android.com/apk/res/android"'
open(r+"layout/yks_widget.xml","w").write('<LinearLayout '+A+' android:id="@+id/w_root" android:layout_width="match_parent" android:layout_height="match_parent" android:orientation="vertical" android:gravity="center" android:padding="8dp" android:background="@drawable/w_bg"><TextView android:id="@+id/w_name" android:layout_width="wrap_content" android:layout_height="wrap_content" android:textColor="#7C9CFF" android:textSize="14sp" android:textStyle="bold"/><TextView android:id="@+id/w_days" android:layout_width="wrap_content" android:layout_height="wrap_content" android:textColor="#EEF0F6" android:textSize="42sp" android:textStyle="bold"/><TextView android:layout_width="wrap_content" android:layout_height="wrap_content" android:text="gün kaldı" android:textColor="#8A92A8" android:textSize="12sp"/></LinearLayout>')
open(r+"drawable/w_bg.xml","w").write('<shape '+A+' android:shape="rectangle"><solid android:color="#161A24"/><corners android:radius="22dp"/><stroke android:width="1dp" android:color="#262C3C"/></shape>')
for k in ("tyt","ayt"):
    open(r+"xml/"+k+"_info.xml","w").write('<appwidget-provider '+A+' android:minWidth="110dp" android:minHeight="110dp" android:updatePeriodMillis="1800000" android:initialLayout="@layout/yks_widget" android:resizeMode="none" android:widgetCategory="home_screen"/>')
def rc(n,k): return '<receiver android:name=".'+n+'" android:exported="true"><intent-filter><action android:name="android.appwidget.action.APPWIDGET_UPDATE"/><action android:name="android.intent.action.DATE_CHANGED"/><action android:name="android.intent.action.TIME_SET"/></intent-filter><meta-data android:name="android.appwidget.provider" android:resource="@xml/'+k+'_info"/></receiver>'
m="android/app/src/main/AndroidManifest.xml"
t=open(m,encoding="utf-8").read()
t=t.replace("</application>",'<receiver android:name=".SwReceiver" android:exported="false"/>'+rc("TytWidget","tyt")+rc("AytWidget","ayt")+'</application>')
t=t.replace("<application",'<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/><application',1)
open(m,"w",encoding="utf-8").write(t)
import re,shutil
if os.path.exists("debug.keystore"):
    os.makedirs(os.path.expanduser("~/.android"),exist_ok=True)
    shutil.copy("debug.keystore",os.path.expanduser("~/.android/debug.keystore"))
sx=r+"values/strings.xml"
x=open(sx,encoding="utf-8").read()
x=re.sub(r'(<string name="(?:app_name|title_activity_main)">)[^<]*',r'\1yks27',x)
open(sx,"w",encoding="utf-8").write(x)
w="www/index.html"
x=open(w,encoding="utf-8").read().replace("__BUILD__",os.environ.get("GITHUB_RUN_NUMBER","0"))
open(w,"w",encoding="utf-8").write(x)
print("patched")
