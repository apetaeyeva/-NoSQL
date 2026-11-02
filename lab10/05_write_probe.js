// Непрерывная запись с w:majority во время отказа. ACK-идентификаторы пишутся в stdout.
// mongosh "mongodb://127.0.0.1:27101,127.0.0.1:27102,127.0.0.1:27103/?replicaSet=rsLab10&serverSelectionTimeoutMS=2000" \
//         --quiet --file 05_write_probe.js | tee probe.log
const c = db.getSiblingDB("university_lab10").grades_probe;
try { c.createIndex({probeId: 1}, {unique: true}); } catch (e) {}
for (let i = 1; i <= 600; i++) {            // ~2 минуты при паузе 200 мс
  const t = new Date().toISOString();
  try {
    c.insertOne({probeId: i, ts: new Date()}, {writeConcern: {w: "majority", wtimeout: 3000}});
    print(t, "ACK", i);
  } catch (e) {
    print(t, "FAIL", i, e.codeName || e.name);   // текст ошибки без URI
  }
  sleep(200);
}
