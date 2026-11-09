// Наблюдатель за ролями узлов, печатает время каждого изменения (t0/t1).
// mongosh --nodb --quiet --file 04_watch_failover.js | tee watch.log
// Запустите ДО остановки primary; остановите вручную по Ctrl+C после возврата узла.
const ports = [27101, 27102, 27103];
function role(p) {
  try {
    const c = new Mongo(`mongodb://127.0.0.1:${p}/?directConnection=true&serverSelectionTimeoutMS=300&connectTimeoutMS=300`);
    const h = c.getDB("admin").hello(); c.close();
    return h.isWritablePrimary ? "PRIMARY" : (h.secondary ? "SECONDARY" : "OTHER");
  } catch (e) { return "DOWN"; }
}
const last = {};
let t0 = null, lostPort = null;
while (true) {
  for (const p of ports) {
    const r = role(p), now = new Date();
    if (last[p] !== r) {
      print(now.toISOString(), "port", p, last[p] || "-", "->", r);
      if (last[p] === "PRIMARY" && r === "DOWN") { t0 = now; lostPort = p; }
      if (t0 && r === "PRIMARY" && p !== lostPort) {
        print(">>> t0 =", t0.toISOString(), " t1 =", now.toISOString(),
              " switchover (watcher precision ~0.3-1 s) =", ((now - t0) / 1000).toFixed(2), "s");
        t0 = null;
      }
      last[p] = r;
    }
  }
  sleep(200);
}
