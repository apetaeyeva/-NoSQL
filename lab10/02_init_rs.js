// mongosh --port 27101 --file 02_init_rs.js
rs.initiate({_id: "rsLab10", members: [
  {_id: 0, host: "127.0.0.1:27101"},
  {_id: 1, host: "127.0.0.1:27102"},
  {_id: 2, host: "127.0.0.1:27103"}]});
// ожидание выбора primary (до 30 с)
for (let i = 0; i < 30 && !db.hello().isWritablePrimary; i++) sleep(1000);
rs.status().members.forEach(m => print(m.name, m.stateStr));
