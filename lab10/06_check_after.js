// Проверка данных после failover / возврата узла / восстановления. Укажите нужную БД через DBNAME.
// mongosh "<uri>" --quiet --eval 'var DBNAME="university_lab10"' --file 06_check_after.js
const name = (typeof DBNAME !== "undefined") ? DBNAME : "university_lab10";
const d = db.getSiblingDB(name);
const ids = d.grades.find({}, {_id: 0, gradeId: 1}).sort({gradeId: 1}).toArray().map(x => x.gradeId);
print("db:", name, " grades count:", ids.length, " max gradeId:", ids[ids.length - 1]);
const s = d.grades.aggregate([{$group: {_id: null, s: {$sum: "$score"}}}]).toArray();
print("sum(score) checksum:", s.length ? s[0].s : null, " (ожидается как после seed)");
const miss = []; for (let i = 1; i <= 20; i++) if (!ids.includes(i)) miss.push(i);
print("missing gradeId 1..20:", miss.length ? miss : "none");
if (name === "university_lab10") {
  const p = d.grades_probe.find({}, {_id: 0, probeId: 1}).sort({probeId: 1}).toArray().map(x => x.probeId);
  const gaps = []; for (let i = 1; i <= p[p.length - 1]; i++) if (!p.includes(i)) gaps.push(i);
  print("probe: stored", p.length, " max probeId:", p[p.length - 1],
        " gaps (не сохранены; сравните с ACK в probe.log):", gaps.length ? gaps : "none");
}
