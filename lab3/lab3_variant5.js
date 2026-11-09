// Лабораторная работа №3, вариант 5 (Онлайн-библиотека). Запуск: mongosh --file lab3_variant5.js
// (или вставляйте блоки по одному в mongosh и снимайте скриншоты).
db = db.getSiblingDB("library_lab3");
db.dropDatabase();

// ===== Задача 1. Создать БД =====
// use library_lab3  (в скрипте переключение уже выполнено выше)

// ===== Задача 2. Создать минимум 4 коллекции (создано 6) =====
db.createCollection("users");
db.createCollection("authors");
db.createCollection("books");
db.createCollection("loans");
db.createCollection("reviews");
db.createCollection("book_events");

// ===== Задача 3. Добавить минимум 25 документов (добавлено 41) =====
db.users.insertMany([{"userId": 1001, "fullName": {"firstName": "Aidar", "lastName": "Serikov"}, "contacts": {"email": "aidar@example.com", "phone": "+7 700 111 22 33"}, "address": {"city": "Almaty", "street": "Abay", "building": 10}, "membership": "standard", "interests": [], "registeredAt": ISODate("2025-09-01T00:00:00Z"), "active": true}, {"userId": 1002, "fullName": {"firstName": "Aliya", "lastName": "Nurova"}, "contacts": {"email": "aliya@example.com", "phone": "+7 701 222 33 44"}, "address": {"city": "Astana", "street": "Kabanbay Batyr", "building": 4}, "membership": "premium", "interests": [], "registeredAt": ISODate("2025-09-15T00:00:00Z"), "active": true}, {"userId": 1003, "fullName": {"firstName": "Dana", "lastName": "Omarova"}, "contacts": {"email": "dana@example.com", "phone": "+7 702 333 44 55"}, "address": {"city": "Almaty", "street": "Satpayev", "building": 22}, "membership": "standard", "interests": [], "registeredAt": ISODate("2025-10-02T00:00:00Z"), "active": true}, {"userId": 1004, "fullName": {"firstName": "Marat", "lastName": "Kenesov"}, "contacts": {"email": "marat@example.com", "phone": "+7 705 444 55 66"}, "address": {"city": "Shymkent", "street": "Tauke Khan", "building": 7}, "membership": "standard", "interests": [], "registeredAt": ISODate("2025-10-20T00:00:00Z"), "active": true}, {"userId": 1005, "fullName": {"firstName": "Zarina", "lastName": "Bekova"}, "contacts": {"email": "zarina@example.com", "phone": "+7 707 555 66 77"}, "address": {"city": "Almaty", "street": "Furmanov", "building": 15}, "membership": "premium", "interests": [], "registeredAt": ISODate("2026-01-10T00:00:00Z"), "active": true}, {"userId": 1006, "fullName": {"firstName": "Timur", "lastName": "Alimov"}, "contacts": {"email": "timur@example.com", "phone": "+7 708 666 77 88"}, "address": {"city": "Astana", "street": "Turan", "building": 31}, "membership": "standard", "interests": [], "registeredAt": ISODate("2026-02-05T00:00:00Z"), "active": true}]);
db.authors.insertMany([{"authorId": 301, "fullName": {"firstName": "Abai", "lastName": "Kunanbaiuly"}, "country": "Kazakhstan", "birthYear": 1845}, {"authorId": 302, "fullName": {"firstName": "Mukhtar", "lastName": "Auezov"}, "country": "Kazakhstan", "birthYear": 1897}, {"authorId": 303, "fullName": {"firstName": "Chinghiz", "lastName": "Aitmatov"}, "country": "Kyrgyzstan", "birthYear": 1928}, {"authorId": 304, "fullName": {"firstName": "Fyodor", "lastName": "Dostoevsky"}, "country": "Russia", "birthYear": 1821}, {"authorId": 305, "fullName": {"firstName": "Isaac", "lastName": "Asimov"}, "country": "USA", "birthYear": 1920}]);
db.books.insertMany([{"bookId": 101, "title": "Book of Words", "authorId": 301, "authorName": "Abai Kunanbaiuly", "genres": ["philosophy", "classic"], "year": 1904, "copiesAvailable": 5, "ratingAvg": 4.8}, {"bookId": 102, "title": "Abai Zholy", "authorId": 302, "authorName": "Mukhtar Auezov", "genres": ["novel", "classic"], "year": 1947, "copiesAvailable": 3, "ratingAvg": 4.7}, {"bookId": 103, "title": "The Day Lasts More Than a Hundred Years", "authorId": 303, "authorName": "Chinghiz Aitmatov", "genres": ["novel", "sci-fi"], "year": 1980, "copiesAvailable": 2, "ratingAvg": 4.5}, {"bookId": 104, "title": "Jamila", "authorId": 303, "authorName": "Chinghiz Aitmatov", "genres": ["novel", "classic"], "year": 1958, "copiesAvailable": 4, "ratingAvg": 4.6}, {"bookId": 105, "title": "Crime and Punishment", "authorId": 304, "authorName": "Fyodor Dostoevsky", "genres": ["novel", "classic", "psychology"], "year": 1866, "copiesAvailable": 6, "ratingAvg": 4.9, "activityLog": [{"userId": 1001, "eventType": "view", "createdAt": ISODate("2026-10-01T09:00:00Z")}, {"userId": 1002, "eventType": "view", "createdAt": ISODate("2026-10-01T10:30:00Z")}, {"userId": 1003, "eventType": "download", "createdAt": ISODate("2026-10-02T12:15:00Z")}]}, {"bookId": 106, "title": "The Idiot", "authorId": 304, "authorName": "Fyodor Dostoevsky", "genres": ["novel", "classic"], "year": 1869, "copiesAvailable": 2, "ratingAvg": 4.4}, {"bookId": 107, "title": "Foundation", "authorId": 305, "authorName": "Isaac Asimov", "genres": ["sci-fi"], "year": 1951, "copiesAvailable": 3, "ratingAvg": 4.6}, {"bookId": 108, "title": "I, Robot", "authorId": 305, "authorName": "Isaac Asimov", "genres": ["sci-fi", "short stories"], "year": 1950, "copiesAvailable": 1, "ratingAvg": 4.3}]);
db.loans.insertMany([{"loanId": 9001, "userId": 1001, "bookId": 105, "loanDate": ISODate("2026-10-01T00:00:00Z"), "dueDate": ISODate("2026-10-15T00:00:00Z"), "returnDate": ISODate("2026-10-12T00:00:00Z"), "status": "returned", "fine": 0, "userSnapshot": {"fullName": "Aidar Serikov", "email": "aidar@example.com", "membership": "standard"}, "bookSnapshot": {"title": "Crime and Punishment", "authorName": "Fyodor Dostoevsky"}}, {"loanId": 9002, "userId": 1001, "bookId": 107, "loanDate": ISODate("2026-10-20T00:00:00Z"), "dueDate": ISODate("2026-11-03T00:00:00Z"), "returnDate": null, "status": "active", "fine": 0, "userSnapshot": {"fullName": "Aidar Serikov", "email": "aidar@example.com", "membership": "standard"}, "bookSnapshot": {"title": "Foundation", "authorName": "Isaac Asimov"}}, {"loanId": 9003, "userId": 1002, "bookId": 101, "loanDate": ISODate("2026-09-20T00:00:00Z"), "dueDate": ISODate("2026-10-04T00:00:00Z"), "returnDate": ISODate("2026-10-03T00:00:00Z"), "status": "returned", "fine": 0, "userSnapshot": {"fullName": "Aliya Nurova", "email": "aliya@example.com", "membership": "premium"}, "bookSnapshot": {"title": "Book of Words", "authorName": "Abai Kunanbaiuly"}}, {"loanId": 9004, "userId": 1002, "bookId": 103, "loanDate": ISODate("2026-10-05T00:00:00Z"), "dueDate": ISODate("2026-10-19T00:00:00Z"), "returnDate": null, "status": "overdue", "fine": 1500, "userSnapshot": {"fullName": "Aliya Nurova", "email": "aliya@example.com", "membership": "premium"}, "bookSnapshot": {"title": "The Day Lasts More Than a Hundred Years", "authorName": "Chinghiz Aitmatov"}}, {"loanId": 9005, "userId": 1003, "bookId": 104, "loanDate": ISODate("2026-10-10T00:00:00Z"), "dueDate": ISODate("2026-10-24T00:00:00Z"), "returnDate": ISODate("2026-10-30T00:00:00Z"), "status": "returned", "fine": 600, "userSnapshot": {"fullName": "Dana Omarova", "email": "dana@example.com", "membership": "standard"}, "bookSnapshot": {"title": "Jamila", "authorName": "Chinghiz Aitmatov"}}, {"loanId": 9006, "userId": 1004, "bookId": 102, "loanDate": ISODate("2026-10-25T00:00:00Z"), "dueDate": ISODate("2026-11-08T00:00:00Z"), "returnDate": null, "status": "overdue", "fine": 300, "userSnapshot": {"fullName": "Marat Kenesov", "email": "marat@example.com", "membership": "standard"}, "bookSnapshot": {"title": "Abai Zholy", "authorName": "Mukhtar Auezov"}}, {"loanId": 9007, "userId": 1005, "bookId": 108, "loanDate": ISODate("2026-11-01T00:00:00Z"), "dueDate": ISODate("2026-11-15T00:00:00Z"), "returnDate": null, "status": "active", "fine": 0, "userSnapshot": {"fullName": "Zarina Bekova", "email": "zarina@example.com", "membership": "premium"}, "bookSnapshot": {"title": "I, Robot", "authorName": "Isaac Asimov"}}, {"loanId": 9008, "userId": 1005, "bookId": 105, "loanDate": ISODate("2026-09-01T00:00:00Z"), "dueDate": ISODate("2026-09-15T00:00:00Z"), "returnDate": ISODate("2026-09-14T00:00:00Z"), "status": "returned", "fine": 0, "userSnapshot": {"fullName": "Zarina Bekova", "email": "zarina@example.com", "membership": "premium"}, "bookSnapshot": {"title": "Crime and Punishment", "authorName": "Fyodor Dostoevsky"}}, {"loanId": 9009, "userId": 1006, "bookId": 106, "loanDate": ISODate("2026-10-28T00:00:00Z"), "dueDate": ISODate("2026-11-11T00:00:00Z"), "returnDate": null, "status": "active", "fine": 0, "userSnapshot": {"fullName": "Timur Alimov", "email": "timur@example.com", "membership": "standard"}, "bookSnapshot": {"title": "The Idiot", "authorName": "Fyodor Dostoevsky"}}, {"loanId": 9010, "userId": 1003, "bookId": 105, "loanDate": ISODate("2026-11-02T00:00:00Z"), "dueDate": ISODate("2026-11-16T00:00:00Z"), "returnDate": null, "status": "active", "fine": 0, "userSnapshot": {"fullName": "Dana Omarova", "email": "dana@example.com", "membership": "standard"}, "bookSnapshot": {"title": "Crime and Punishment", "authorName": "Fyodor Dostoevsky"}}]);
db.reviews.insertMany([{"reviewId": 7001, "bookId": 105, "userId": 1001, "rating": 5, "text": "Powerful psychological novel", "createdAt": ISODate("2026-10-13T00:00:00Z")}, {"reviewId": 7002, "bookId": 101, "userId": 1002, "rating": 5, "text": "Wisdom for every age", "createdAt": ISODate("2026-10-04T00:00:00Z")}, {"reviewId": 7003, "bookId": 104, "userId": 1003, "rating": 4, "text": "Warm and poetic", "createdAt": ISODate("2026-10-31T00:00:00Z")}, {"reviewId": 7004, "bookId": 103, "userId": 1002, "rating": 4, "text": "Deep and sad", "createdAt": ISODate("2026-10-22T00:00:00Z")}, {"reviewId": 7005, "bookId": 105, "userId": 1005, "rating": 5, "text": "Reread it twice", "createdAt": ISODate("2026-09-16T00:00:00Z")}, {"reviewId": 7006, "bookId": 108, "userId": 1005, "rating": 3, "text": "Short but thin", "createdAt": ISODate("2026-11-03T00:00:00Z")}]);
db.book_events.insertMany([{"eventId": 50001, "bookId": 107, "userId": 1001, "eventType": "view", "createdAt": ISODate("2026-10-19T18:00:00Z")}, {"eventId": 50002, "bookId": 107, "userId": 1003, "eventType": "view", "createdAt": ISODate("2026-10-20T08:40:00Z")}, {"eventId": 50003, "bookId": 103, "userId": 1002, "eventType": "download", "createdAt": ISODate("2026-10-04T21:10:00Z")}, {"eventId": 50004, "bookId": 108, "userId": 1005, "eventType": "view", "createdAt": ISODate("2026-10-31T19:30:00Z")}, {"eventId": 50005, "bookId": 102, "userId": 1004, "eventType": "view", "createdAt": ISODate("2026-10-24T11:00:00Z")}, {"eventId": 50006, "bookId": 106, "userId": 1006, "eventType": "download", "createdAt": ISODate("2026-10-27T15:20:00Z")}]);
db.users.countDocuments()
db.authors.countDocuments()
db.books.countDocuments()
db.loans.countDocuments()
db.reviews.countDocuments()
db.book_events.countDocuments();

// ===== Задача 4. Создать Embedded Document (preferences во вложенном документе) =====
db.users.updateOne({"userId": 1001}, {"$set": {"preferences": {"language": "kk", "notify": {"email": true, "sms": false}}}});
db.users.find({"userId": 1001}, {"_id": 0, "userId": 1, "preferences": 1}).forEach(printjson);

// ===== Задача 5. Создать массив простых значений (interests) =====
db.users.updateOne({"userId": 1001}, {"$set": {"interests": ["classic", "sci-fi", "history"]}});
db.users.find({"userId": 1001}, {"_id": 0, "userId": 1, "interests": 1}).forEach(printjson);

// ===== Задача 6. Создать массив документов (editions у книг 105 и 103) =====
db.books.updateOne({"bookId": 105}, {"$set": {"editions": [{"year": 2002, "publisher": "Penguin", "pages": 576}, {"year": 2015, "publisher": "Vintage", "pages": 545}]}});
db.books.updateOne({"bookId": 103}, {"$set": {"editions": [{"year": 1983, "publisher": "Indiana University Press", "pages": 352}, {"year": 2008, "publisher": "Penguin", "pages": 336}]}});
db.books.find({"editions": {"$exists": true}}, {"_id": 0, "bookId": 1, "editions": 1}).forEach(printjson);

// ===== Задача 7. Поиск через dot notation =====
db.users.find({"address.city": "Almaty"}, {"_id": 0, "userId": 1, "fullName.firstName": 1, "contacts.email": 1}).forEach(printjson);

// ===== Задача 8. Использовать $push =====
db.users.updateOne({"userId": 1001}, {"$push": {"interests": "poetry"}});
db.users.find({"userId": 1001}, {"_id": 0, "interests": 1}).forEach(printjson);

// ===== Задача 9. Использовать $pull =====
db.users.updateOne({"userId": 1001}, {"$pull": {"interests": "history"}});
db.users.find({"userId": 1001}, {"_id": 0, "interests": 1}).forEach(printjson);

// ===== Задача 10. Использовать $addToSet (дубль не добавится, новое значение добавится) =====
db.users.updateOne({"userId": 1001}, {"$addToSet": {"interests": "poetry"}});
db.users.updateOne({"userId": 1001}, {"$addToSet": {"interests": "fantasy"}});
db.users.find({"userId": 1001}, {"_id": 0, "interests": 1}).forEach(printjson);

// ===== Задача 11. Использовать $elemMatch =====
db.books.find({"editions": {"$elemMatch": {"publisher": "Penguin", "year": {"$gte": 2000}}}}, {"_id": 0, "bookId": 1, "title": 1}).forEach(printjson);

// ===== Задача 12. Реализовать связь 1:1 (User - contacts/address через embedding) =====
db.users.find({"contacts.email": "aidar@example.com"}, {"_id": 0, "userId": 1, "fullName": 1, "contacts": 1, "address": 1}).forEach(printjson);

// ===== Задача 13. Реализовать 1:N через embedding (Book - editions) =====
db.books.find({"bookId": 105}, {"_id": 0, "title": 1, "editions": 1}).forEach(printjson);

// ===== Задача 14. Реализовать 1:N через referencing (Author - Book по authorId) =====
db.books.find({"authorId": 305}, {"_id": 0, "bookId": 1, "title": 1, "authorId": 1}).forEach(printjson);

// ===== Задача 15. Реализовать N:M (новая выдача связывает User и Book) =====
db.loans.insertOne({"loanId": 9011, "userId": 1006, "bookId": 107, "loanDate": ISODate("2026-11-08T00:00:00Z"), "dueDate": ISODate("2026-11-22T00:00:00Z"), "returnDate": null, "status": "active", "fine": 0, "userSnapshot": {"fullName": "Timur Alimov", "email": "timur@example.com", "membership": "standard"}, "bookSnapshot": {"title": "Foundation", "authorName": "Isaac Asimov"}});
db.loans.find({"loanId": 9011}, {"_id": 0, "loanId": 1, "userId": 1, "bookId": 1, "status": 1}).forEach(printjson);

// ===== Задача 16. Выполнить запрос по ссылке ($lookup: автор вместе со своими книгами) =====
db.authors.aggregate([{"$match": {"authorId": 303}}, {"$lookup": {"from": "books", "localField": "authorId", "foreignField": "authorId", "as": "books"}}, {"$project": {"_id": 0, "fullName": 1, "books.title": 1}}]).forEach(printjson);

// ===== Задача 17. Запрос к промежуточной коллекции (активные выдачи читателя) =====
db.loans.find({"userId": 1001, "status": "active"}, {"_id": 0, "loanId": 1, "bookId": 1, "dueDate": 1}).forEach(printjson);

// ===== Задача 18. Использовать $gte/$lte =====
db.books.find({"year": {"$gte": 1900, "$lte": 1999}}, {"_id": 0, "title": 1, "year": 1}).forEach(printjson);

// ===== Задача 19. Использовать $in =====
db.books.find({"genres": {"$in": ["sci-fi", "psychology"]}}, {"_id": 0, "bookId": 1, "title": 1}).forEach(printjson);

// ===== Задача 20. Использовать $or =====
db.loans.find({"$or": [{"status": "overdue"}, {"fine": {"$gt": 0}}]}, {"_id": 0, "loanId": 1, "userId": 1, "status": 1, "fine": 1}).forEach(printjson);

// ===== Задача 21. Сортировка (по рейтингу, убывание) =====
db.books.find({}, {"_id": 0, "title": 1, "ratingAvg": 1}).sort({"ratingAvg": -1}).forEach(printjson);

// ===== Задача 22. Проекция =====
db.users.find({}, {"_id": 0, "userId": 1, "fullName.lastName": 1, "contacts.email": 1}).forEach(printjson);

// ===== Задача 23. Использовать limit() (топ-3 книги) =====
db.books.find({}, {"_id": 0, "title": 1, "ratingAvg": 1}).sort({"ratingAvg": -1}).limit(3).forEach(printjson);

// ===== Задача 24. Продемонстрировать денормализацию и Snapshot (смена email не меняет снимок в выдаче) =====
db.users.updateOne({"userId": 1001}, {"$set": {"contacts.email": "aidar.new@example.com"}});
db.users.find({"userId": 1001}, {"_id": 0, "userId": 1, "contacts.email": 1}).forEach(printjson);
db.loans.find({"loanId": 9001}, {"_id": 0, "loanId": 1, "userSnapshot": 1, "bookSnapshot": 1}).forEach(printjson);

// ===== Задача 25. Найти и исправить Unbounded Array (activityLog -> коллекция book_events) =====
db.books.find({"activityLog": {"$exists": true}}, {"_id": 0, "bookId": 1, "activityLog": 1}).forEach(printjson);
// перенос записей activityLog в отдельную коллекцию
db.book_events.insertMany([
  {eventId: 50007, bookId: 105, userId: 1001, eventType: "view", createdAt: ISODate("2026-10-01T09:00:00Z")},
  {eventId: 50008, bookId: 105, userId: 1002, eventType: "view", createdAt: ISODate("2026-10-01T10:30:00Z")},
  {eventId: 50009, bookId: 105, userId: 1003, eventType: "download", createdAt: ISODate("2026-10-02T12:15:00Z")}
]);
db.books.updateOne({"bookId": 105}, {"$unset": {"activityLog": ""}});
db.book_events.find({"bookId": 105}, {"_id": 0, "eventId": 1, "userId": 1, "eventType": 1}).forEach(printjson);
db.books.find({"bookId": 105}, {"_id": 0, "bookId": 1, "activityLog": 1}).forEach(printjson);

