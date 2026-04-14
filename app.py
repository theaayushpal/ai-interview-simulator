from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
import os
import json
import re

app = Flask(__name__)
CORS(app)
@app.route("/")
@app.route("/api/test")
def test():
    return jsonify({"message": "API working"})
# ─── Gemini Setup ────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")          # set via env var
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None   # fallback to mock responses

# ─── Full Question Bank ───────────────────────────────────────────────────────
QUESTION_BANK = {
    "python": {
        "easy": [
            "What is the difference between a list and a tuple in Python?",
            "What are Python's built-in data types?",
            "What is the difference between `==` and `is` in Python?",
            "How do you create a virtual environment in Python?",
            "What is PEP 8?",
            "What is the difference between `append()` and `extend()` in a list?",
            "What is a Python dictionary and how do you access values?",
            "What does the `len()` function do?",
            "How do you handle exceptions in Python?",
            "What is the difference between `break` and `continue`?",
        ],
        "medium": [
            "What is a decorator in Python? Write an example.",
            "Explain list comprehensions with an example.",
            "What is the difference between `*args` and `**kwargs`?",
            "What are lambda functions? When would you use one?",
            "Explain the concept of generators and `yield` in Python.",
            "What is the Global Interpreter Lock (GIL)?",
            "What is the difference between shallow copy and deep copy?",
            "How does Python's garbage collection work?",
            "What are Python's `__init__` and `__str__` dunder methods?",
            "Explain the difference between `@staticmethod` and `@classmethod`.",
        ],
        "hard": [
            "Explain Python's memory management and reference counting.",
            "What is a metaclass in Python? Give a use case.",
            "How does the `asyncio` event loop work in Python?",
            "Explain the MRO (Method Resolution Order) in Python's multiple inheritance.",
            "What are context managers and how do you implement one using `__enter__` and `__exit__`?",
            "How would you profile and optimize a slow Python script?",
            "Explain Python descriptors and how they power `@property`.",
            "What is the difference between `multiprocessing` and `multithreading` in Python?",
            "How do you implement a thread-safe singleton in Python?",
            "Explain coroutines vs threads vs processes in Python.",
        ],
    },
    "data structures": {
        "easy": [
            "What is the difference between an array and a linked list?",
            "What is a stack? Name two real-life examples.",
            "What is a queue? How is it different from a stack?",
            "What is Big-O notation and why does it matter?",
            "What is a binary search? What is its time complexity?",
            "What is a hash table? How does it handle collisions?",
            "What is the difference between BFS and DFS?",
            "What is a tree? Define root, leaf, and height.",
            "What is a circular linked list?",
            "What is the time complexity of inserting into a Python list?",
        ],
        "medium": [
            "Explain how a hash map works internally.",
            "What is a binary search tree? How do you check if a BST is valid?",
            "What is the difference between a min-heap and a max-heap?",
            "How would you implement a queue using two stacks?",
            "What is dynamic programming? Explain with the Fibonacci example.",
            "What is the difference between stable and unstable sorting algorithms?",
            "Explain the merge sort algorithm and its time complexity.",
            "What is a graph? Explain adjacency list vs adjacency matrix.",
            "How does quicksort work? What is its worst-case time complexity?",
            "What is a trie? What is it used for?",
        ],
        "hard": [
            "Implement LRU Cache using a doubly linked list and hash map.",
            "Explain Dijkstra's algorithm and its time complexity.",
            "What is a B-tree and why is it used in databases?",
            "How would you detect a cycle in a directed graph?",
            "Explain the Union-Find data structure and its applications.",
            "What is the difference between Prim's and Kruskal's algorithm?",
            "Explain how a red-black tree maintains balance.",
            "What is a segment tree? When would you use it over a Fenwick tree?",
            "How would you serialize and deserialize a binary tree?",
            "Explain Floyd-Warshall algorithm and when to use it over Dijkstra's.",
        ],
    },
    "web development": {
        "easy": [
            "What is the difference between GET and POST HTTP methods?",
            "What does HTML stand for and what is its purpose?",
            "What is CSS and how does it differ from HTML?",
            "What is a cookie? How is it different from localStorage?",
            "What is the difference between HTTP and HTTPS?",
            "What is a REST API?",
            "What does a 404 error mean? What about 500?",
            "What is responsive design?",
            "What is the DOM (Document Object Model)?",
            "What is the difference between `<div>` and `<span>`?",
        ],
        "medium": [
            "What is CORS and why is it needed?",
            "Explain the difference between authentication and authorization.",
            "What is a JWT (JSON Web Token)? How does it work?",
            "What is the difference between SQL and NoSQL databases?",
            "Explain the event loop in JavaScript.",
            "What is a RESTful API? What are its key constraints?",
            "What is the difference between `Promise` and `async/await` in JS?",
            "What is webpack and why is it used?",
            "Explain the CSS box model.",
            "What is server-side rendering vs client-side rendering?",
        ],
        "hard": [
            "How would you design a URL shortener like bit.ly?",
            "Explain how HTTPS works, including the TLS handshake.",
            "What is the CAP theorem in distributed systems?",
            "How do you prevent SQL injection and XSS attacks?",
            "What is WebSockets and how does it differ from HTTP polling?",
            "How would you scale a web application to handle millions of users?",
            "Explain OAuth 2.0 flow in detail.",
            "What is a CDN and how does it improve performance?",
            "What are microservices? What are the tradeoffs vs monolith?",
            "How does browser caching work and how do you control it?",
        ],
    },
    "flask & backend": {
        "easy": [
            "What is Flask and how is it different from Django?",
            "How do you define a route in Flask?",
            "What does `@app.route()` do in Flask?",
            "How do you return JSON from a Flask route?",
            "What is `request.get_json()` used for in Flask?",
            "What HTTP methods does Flask support?",
            "What is Flask-CORS and why do we use it?",
            "What does `app.run(debug=True)` do?",
            "How do you read URL query parameters in Flask?",
            "What is a virtual environment and why use one with Flask?",
        ],
        "medium": [
            "What is the difference between `request.args`, `request.form`, and `request.json` in Flask?",
            "How do you handle 404 and 500 errors in Flask?",
            "What is a Blueprint in Flask and when would you use it?",
            "How do you connect Flask to a SQLite database using SQLAlchemy?",
            "Explain how Flask handles request context and application context.",
            "How would you add authentication to a Flask API?",
            "What is middleware in Flask? Give an example using `before_request`.",
            "How do you deploy a Flask app to production using gunicorn?",
            "What is the difference between `jsonify()` and `json.dumps()` in Flask?",
            "How do you test Flask routes using pytest?",
        ],
        "hard": [
            "How would you implement rate limiting in a Flask API?",
            "How do you handle file uploads securely in Flask?",
            "Explain how to implement JWT authentication from scratch in Flask.",
            "How would you structure a large Flask application using the Application Factory pattern?",
            "How do you implement background tasks in Flask using Celery?",
            "What are the security considerations when deploying a Flask API?",
            "How would you implement database migrations in Flask using Alembic?",
            "Explain caching strategies you can use with Flask.",
            "How would you build a real-time feature in Flask using Server-Sent Events?",
            "How do you handle concurrent requests in Flask with async support?",
        ],
    },
    "oops & design": {
        "easy": [
            "What are the four pillars of Object-Oriented Programming?",
            "What is the difference between a class and an object?",
            "What is inheritance and why is it useful?",
            "What is encapsulation? Give a real-world example.",
            "What is polymorphism? Give an example.",
            "What is an abstract class?",
            "What is the difference between method overloading and method overriding?",
            "What is a constructor?",
            "What is the difference between public, private, and protected access modifiers?",
            "What is an interface and how does it differ from an abstract class?",
        ],
        "medium": [
            "Explain the SOLID principles in OOP.",
            "What is the Singleton design pattern? When would you use it?",
            "What is the Factory design pattern?",
            "What is the Observer design pattern? Give a real-world example.",
            "What is composition over inheritance?",
            "What is the Decorator design pattern (not Python decorator)?",
            "Explain the difference between coupling and cohesion.",
            "What is the MVC (Model-View-Controller) pattern?",
            "What is dependency injection and why is it useful?",
            "What is the difference between aggregation and composition in OOP?",
        ],
        "hard": [
            "Explain the Strategy design pattern with a real example.",
            "How would you refactor a God Object into smaller, cohesive classes?",
            "What is the difference between the Proxy and Decorator patterns?",
            "Explain the CQRS (Command Query Responsibility Segregation) pattern.",
            "How does the Repository pattern help in separating concerns?",
            "What is eventual consistency and how does it affect design?",
            "Compare the Adapter, Facade, and Bridge design patterns.",
            "How would you design a parking lot system using OOP?",
            "Explain the Event Sourcing pattern.",
            "What is Domain-Driven Design (DDD)?",
        ],
    },
    "databases": {
        "easy": [
            "What is the difference between SQL and NoSQL?",
            "What is a primary key? What is a foreign key?",
            "What does CRUD stand for?",
            "What is a JOIN in SQL? Name its types.",
            "What is normalization? What are 1NF, 2NF, 3NF?",
            "What is an index in a database and why is it used?",
            "What is the difference between DELETE, TRUNCATE, and DROP?",
            "What is a transaction in a database?",
            "What does ACID stand for in databases?",
            "What is the difference between WHERE and HAVING in SQL?",
        ],
        "medium": [
            "Explain database indexing strategies — B-tree vs hash index.",
            "What is a stored procedure and when would you use one?",
            "What is the N+1 query problem and how do you fix it?",
            "Explain optimistic vs pessimistic locking.",
            "What is database sharding and when would you use it?",
            "Explain the difference between INNER JOIN and OUTER JOIN.",
            "What is a view in SQL and when is it useful?",
            "What is the difference between clustered and non-clustered indexes?",
            "How does Redis differ from a relational database?",
            "What are triggers in SQL?",
        ],
        "hard": [
            "How would you design a database schema for a Twitter-like app?",
            "Explain the two-phase commit protocol.",
            "What is the difference between CAP theorem and PACELC?",
            "How would you handle millions of read requests on a single database?",
            "What is a write-ahead log (WAL) in databases?",
            "Explain MVCC (Multi-Version Concurrency Control).",
            "How does consistent hashing work in distributed databases?",
            "What is a materialized view and how does it differ from a regular view?",
            "How would you design a database for a ride-sharing app like Uber?",
            "Explain database replication strategies: master-slave vs master-master.",
        ],
    },
    "hr & behavioural": {
        "easy": [
            "Tell me about yourself.",
            "Why do you want to work here?",
            "What are your greatest strengths?",
            "What is your biggest weakness?",
            "Where do you see yourself in 5 years?",
            "Why did you choose computer science/engineering?",
            "Describe a project you are proud of.",
            "What motivates you to work hard?",
            "How do you handle stress and pressure?",
            "Are you a team player or do you prefer working alone?",
        ],
        "medium": [
            "Describe a time you faced a conflict with a teammate and how you resolved it.",
            "Tell me about a time you failed and what you learned from it.",
            "Describe a challenging problem you solved creatively.",
            "Give an example of when you had to meet a tight deadline.",
            "Tell me about a time you had to learn something new quickly.",
            "How do you prioritize tasks when you have multiple deadlines?",
            "Describe a time you showed leadership.",
            "Tell me about a time you disagreed with your manager. What did you do?",
            "Give an example of how you've contributed to a team's success.",
            "Describe a situation where you had to adapt to a major change.",
        ],
        "hard": [
            "Where do you see the field of software engineering in 10 years?",
            "How would you handle a situation where you discovered a critical bug right before a product launch?",
            "Describe a time you had to make a difficult decision with incomplete information.",
            "How do you stay updated with rapidly changing technology?",
            "Tell me about a time you had to convince stakeholders of a technical decision they initially opposed.",
            "How would you handle a situation where your team's code quality is consistently poor?",
            "Describe your approach to mentoring a junior developer.",
            "Tell me about a time you had to sacrifice code quality for speed. How did you manage the technical debt?",
            "How do you evaluate whether a new technology is worth adopting?",
            "Describe a time you significantly improved a process or system.",
        ],
    },
}

# ─── Model Answers for evaluation fallback ───────────────────────────────────
MODEL_ANSWERS = {
    "What is the difference between a list and a tuple in Python?":
        "Lists are mutable (can be changed after creation) while tuples are immutable. Lists use square brackets [] and tuples use parentheses (). Tuples are faster and used for fixed data, lists for dynamic data.",
    "What is a decorator in Python? Write an example.":
        "A decorator is a function that wraps another function to extend its behavior without modifying it. Example: @timer decorator that measures execution time. They use the @syntax and are heavily used for logging, authentication, and caching.",
    "What is CORS and why is it needed?":
        "CORS (Cross-Origin Resource Sharing) is a browser security mechanism that restricts web pages from making requests to a different domain than the one that served the page. It's needed to allow frontend apps hosted on one origin to call APIs on another origin. Servers add Access-Control-Allow-Origin headers to permit specific origins.",
    "What are the four pillars of Object-Oriented Programming?":
        "Encapsulation (bundling data and methods, hiding internal state), Inheritance (child class inheriting properties from parent), Polymorphism (same interface, different behavior), and Abstraction (hiding complex implementation details behind simple interfaces).",
    "Tell me about yourself.":
        "Structure: Start with your background (degree, year), mention 1-2 relevant projects or internships, highlight key technical skills, and end with why you're interested in this role. Keep it to 60-90 seconds and tailor it to the company.",
}

# ─── Tips Bank ────────────────────────────────────────────────────────────────
TIPS_BANK = {
    "python": [
        "Master the basics: list/dict/set comprehensions are asked in almost every Python interview.",
        "Understand mutability — know which types are mutable (list, dict, set) vs immutable (int, str, tuple).",
        "Practice decorators and generators — they are favourite medium/hard interview topics.",
        "Know the difference between `deepcopy` and `copy` — a classic gotcha question.",
        "Be comfortable with OOP in Python: `__init__`, `__str__`, `@property`, classmethods.",
        "Understand `*args` and `**kwargs` — very commonly asked.",
        "Practice writing clean, Pythonic code — avoid C-style loops when list comprehensions work.",
    ],
    "data structures": [
        "Know Big-O for all common operations: array, linked list, hash map, BST, heap.",
        "Practice implementing linked list, stack, queue from scratch — interviewers love this.",
        "Understand when to use each structure: hash map for O(1) lookup, heap for min/max queries.",
        "Binary search is used in many non-obvious problems — practice recognizing it.",
        "DFS and BFS are fundamental — practice both recursive and iterative DFS.",
        "Dynamic programming = recursion + memoization. Start with Fibonacci, then knapsack.",
        "For graphs, always clarify: directed or undirected? weighted? can have cycles?",
    ],
    "web development": [
        "Understand the full HTTP request-response cycle — it underpins everything.",
        "Know common HTTP status codes: 200, 201, 400, 401, 403, 404, 500.",
        "REST principles: statelessness, uniform interface, resource-based URLs — memorize these.",
        "CSS specificity and box model trip up many candidates — review them.",
        "JavaScript async (callbacks, Promises, async/await) is tested in almost every frontend role.",
        "Security basics: always know XSS, CSRF, SQL injection and their mitigations.",
        "Practice designing simple systems (URL shortener, chat app) — system design is increasingly common.",
    ],
    "flask & backend": [
        "Know all HTTP methods: GET (read), POST (create), PUT (update), DELETE (delete), PATCH (partial update).",
        "Understand Flask's request object: `request.args`, `request.json`, `request.form`, `request.files`.",
        "Flask-CORS is essential for any frontend-backend separation — know why browsers block cross-origin requests.",
        "Always validate and sanitize request data before using it — never trust user input.",
        "Use environment variables for secrets (API keys, DB passwords) — never hardcode them.",
        "Know how to structure a Flask response: status code + JSON body + headers.",
        "Practice error handling with `@app.errorhandler` for 404 and 500.",
    ],
    "oops & design": [
        "Memorize SOLID principles — Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion.",
        "The three most asked design patterns: Singleton, Factory, Observer. Know them cold.",
        "Prefer composition over inheritance — it leads to more flexible, testable code.",
        "For system design questions, always start with clarifying requirements before jumping to solutions.",
        "MVC pattern is fundamental — know how Model, View, and Controller interact.",
        "Practice drawing class diagrams — interviewers often ask you to design a system on a whiteboard.",
        "Dependency injection makes code testable — understand why it matters.",
    ],
    "databases": [
        "Master SQL JOINs (INNER, LEFT, RIGHT, FULL) — draw Venn diagrams to remember.",
        "Understand indexes: they speed up reads but slow down writes — always a trade-off.",
        "ACID properties (Atomicity, Consistency, Isolation, Durability) are asked in every DB interview.",
        "Know when to use NoSQL (flexible schema, high scale) vs SQL (relationships, ACID guarantees).",
        "The N+1 problem is a classic — always know how to fix it with JOIN or eager loading.",
        "Practice writing GROUP BY, HAVING, subqueries, and window functions in SQL.",
        "Normalization vs denormalization trade-offs: normalized = less redundancy, denormalized = faster reads.",
    ],
    "hr & behavioural": [
        "Use the STAR method for every behavioural question: Situation, Task, Action, Result.",
        "Prepare 5-6 strong stories from your projects/life — they can be adapted to many questions.",
        "Research the company: know their product, recent news, mission, and values.",
        "Your 'Tell me about yourself' should be practiced until it flows naturally — it's almost always the opener.",
        "Weakness answers must be genuine but show self-awareness and growth — avoid fake weaknesses like 'I work too hard'.",
        "Always end interviews by asking 2-3 thoughtful questions — it shows genuine interest.",
        "Body language matters: make eye contact, sit straight, smile — especially in online interviews.",
    ],
}

def get_questions_for(topic: str, difficulty: str) -> list:
    """Get question list for a given topic and difficulty."""
    bank = QUESTION_BANK.get(topic, {})
    return bank.get(difficulty, bank.get("medium", ["Describe your experience with " + topic + "."]))

def get_tips_for(topic: str) -> list:
    """Get tips for a given topic."""
    return TIPS_BANK.get(topic, [
        "Study the fundamentals of this topic thoroughly.",
        "Practice explaining concepts out loud to yourself.",
        "Use the STAR method for behavioural questions.",
        "Prepare concrete examples from your own projects.",
        "Ask clarifying questions before answering in interviews.",
    ])

def call_ai(prompt: str) -> str:
    """Call Gemini if key available, else return a placeholder."""
    if model:
        response = model.generate_content(prompt)
        return response.text
    return "[AI response — set GEMINI_API_KEY to enable live answers]"


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")


# GET  /api/topics  — list available interview topics
@app.route("/api/topics", methods=["GET"])
def get_topics():
    topics = list(QUESTION_BANK.keys())
    return jsonify({"topics": topics, "count": len(topics)}), 200


# POST /api/question  — generate an interview question
# Body: { "topic": "python", "difficulty": "easy|medium|hard" }
@app.route("/api/question", methods=["POST"])
def generate_question():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    topic      = data.get("topic", "general").lower()
    difficulty = data.get("difficulty", "medium")

    prompt = (
        f"Generate a single {difficulty} difficulty technical interview question "
        f"on the topic: {topic}. "
        "Return ONLY the question, no numbering or extra text."
    )

    if model:
        question = call_ai(prompt)
    else:
        import random
        questions = get_questions_for(topic, difficulty)
        question = random.choice(questions)

    return jsonify({"question": question, "topic": topic, "difficulty": difficulty}), 200


# POST /api/evaluate  — evaluate the user's answer
# Body: { "question": "...", "answer": "...", "topic": "python" }
@app.route("/api/evaluate", methods=["POST"])
def evaluate_answer():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    question = data.get("question", "")
    answer   = data.get("answer", "")
    topic    = data.get("topic", "general")

    if not question or not answer:
        return jsonify({"error": "Both 'question' and 'answer' are required"}), 422

    prompt = (
        f"You are a strict but fair technical interviewer evaluating a candidate's answer.\n\n"
        f"Topic: {topic}\n"
        f"Question: {question}\n"
        f"Candidate's Answer: {answer}\n\n"
        "Respond with valid JSON only (no markdown) in this exact format:\n"
        '{"score": <0-10>, "feedback": "<2-3 sentences>", '
        '"strengths": ["..."], "improvements": ["..."], "model_answer": "<ideal answer>"}'
    )

    if model:
        raw = call_ai(prompt)
        # strip possible markdown fences
        raw = re.sub(r"```json|```", "", raw).strip()
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            result = {
                "score": 7,
                "feedback": raw[:300],
                "strengths": ["Attempted an answer"],
                "improvements": ["Could not parse structured feedback"],
                "model_answer": "N/A",
            }
    else:
        model_ans = MODEL_ANSWERS.get(question, f"A strong answer to '{question[:60]}...' would clearly define the concept, give an example, and mention trade-offs or real-world use.")
        result = {
            "score": 6,
            "feedback": "Decent attempt! Focus on being more precise and adding a concrete example. Interviewers love when you back up theory with real scenarios.",
            "strengths": ["You attempted to answer the question", "Some relevant points mentioned"],
            "improvements": ["Add a concrete code example or real-world scenario", "Structure your answer: definition → example → trade-offs", "Mention edge cases or common pitfalls"],
            "model_answer": model_ans,
        }

    return jsonify(result), 200


# GET /api/tips?topic=python  — get interview tips for a topic
@app.route("/api/tips", methods=["GET"])
def get_tips():
    topic = request.args.get("topic", "general")
    prompt = (
        f"Give 5 short, actionable interview tips for the topic: {topic}. "
        "Return only a JSON array of strings, e.g. [\"tip1\", \"tip2\", ...]"
    )
    if model:
        raw = call_ai(prompt)
        raw = re.sub(r"```json|```", "", raw).strip()
        try:
            tips = json.loads(raw)
        except Exception:
            tips = [raw]
    else:
        tips = get_tips_for(topic)
    return jsonify({"topic": topic, "tips": tips}), 200


# DELETE /api/session  — reset / end session (stateless demo)
@app.route("/api/session", methods=["DELETE"])
def end_session():
    return jsonify({"message": "Session ended. Good luck with your interview!"}), 200


# ─── Error handlers ──────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "HTTP method not allowed on this route"}), 405


if __name__ == "__main__":
    app.run(debug=True, port=5000)
