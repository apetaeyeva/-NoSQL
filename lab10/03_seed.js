// Вариант 1: Электронный журнал, коллекция grades (оценки студентов), 20 синтетических документов.
// mongosh "mongodb://127.0.0.1:27101,127.0.0.1:27102,127.0.0.1:27103/?replicaSet=rsLab10" --file 03_seed.js
const d = db.getSiblingDB("university_lab10");
d.grades.drop();
d.grades.createIndex({gradeId: 1}, {unique: true});
const subjects = ["NoSQL", "Databases", "Algorithms", "Python"];
const docs = [];
for (let i = 1; i <= 20; i++) {
  docs.push({gradeId: i, studentId: 1000 + ((i - 1) % 5) + 1, subject: subjects[i % 4],
             score: 60 + (i * 7) % 41, gradedAt: new Date(Date.UTC(2026, 8, 1 + i))});
}
const r = d.grades.insertMany(docs, {writeConcern: {w: "majority", wtimeout: 5000}});
print("inserted:", Object.keys(r.insertedIds).length);
print("count:", d.grades.countDocuments(), " max gradeId:", d.grades.find().sort({gradeId: -1}).limit(1).next().gradeId);
print("sum(score) checksum:", d.grades.aggregate([{$group: {_id: null, s: {$sum: "$score"}}}]).next().s);
