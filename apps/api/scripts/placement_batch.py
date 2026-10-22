"""Original small-batch drafts; no reviewer, release or learner DB writes.

Run build once, validate repeatedly, and inventory after editing candidates.
Candidate JSON is the review artifact, never generated at application runtime.
"""
import argparse
import json
from pathlib import Path
from app.config import REPO_ROOT
from app.schemas.publication import QUALITY_CHECKS
from app.services.content_registry import digest
from scripts.content_checks.bundle import validate_candidate

ROOT = REPO_ROOT / "data/content-approvals/phase5"
STAMP = "2026-10-22T00:00:00Z"  # Authoring revision date, not a human review time.


def numeric(key, prompt, answer, explanation, **proof):
    return {"key": key, "kind": "numeric", "prompt": prompt, "explanation": explanation,
            "contract": {"answer": str(answer), "tolerance": "0", "unit": "", "rounding": "none",
                         "boundary": "inclusive", "representation": "decimal", **proof}}


def choice(key, prompt, correct, wrong, explanation):
    # Neutral identities must not reveal which option is the answer. Vary the
    # answer position deterministically; never encode correctness in public IDs.
    right="a" if int(digest(key)[:2],16)%2==0 else "b"
    return {"key": key, "kind": "single_choice", "prompt": prompt, "explanation": explanation,
            "contract": {"choices": {"a":correct if right=="a" else wrong,"b":correct if right=="b" else wrong}, "correct": [right]}}


def code(key, prompt, expression, cases, explanation, parameters=None):
    parameters = parameters or ["value"]
    return {"key": key, "kind": "python", "prompt": prompt, "explanation": explanation,
            "contract": {"mode": "function", "function_name": "solve", "parameters": parameters,
                         "starter_code": f"def solve({', '.join(parameters)}):\n    # Replace pass with your return expression.\n    pass",
                         "reference_solution": f"def solve({', '.join(parameters)}):\n    return {expression}",
                         "tests": [{"name": f"case-{n}", "args": args, "expected": expected} for n, (args, expected) in enumerate(cases)],
                         "sample_tests": [{"name": "public", "args": cases[0][0], "expected": cases[0][1]}],
                         "negative_solutions": [f"def solve({', '.join(parameters)}):\n    return 0"]}}


def reflection(key, prompt, example, rubric):
    return {"key": key, "kind": "reflection", "prompt": prompt, "explanation": "Use the rubric to inspect your own explanation; no correctness score is assigned.",
            "contract": {"example": example, "rubric": rubric}}


def authored():
    # These explanations/examples/questions are original Forge drafts. Reference
    # publishers did not review them; no source prose or illustrations are copied.
    return {
      "quantitative-aptitude": {
        "intuition": "An expression is an instruction with a shared reading order. A bill for a fixed delivery charge plus several identical items should multiply the item cost first; otherwise the delivery charge would be multiplied too. Brackets make a group explicit. Work inside groups first, then powers, multiplication/division from left to right, then addition/subtraction from left to right. Multiplication does not outrank division; they share a level.",
        "worked": "A stationery order has a ₹4 delivery charge and three ₹2 pencils. The total is 4 + 3 × 2. First the pencils cost 6; then add delivery: 4 + 6 = ₹10. By contrast, (4 + 3) × 2 = 14: the brackets change the instruction. For signed values, a temperature of −3°C rising by 5°C becomes 2°C. Estimate before calculating: the order must cost more than the ₹6 pencils, so a result below ₹6 cannot fit this story.",
        "practice": "Guided: evaluate 9 − 2 × 3. Mark multiplication first: 2 × 3 = 6, then 9 − 6 = 3. Independent: a ₹5 booking fee plus four ₹3 tickets costs how much? Stop before opening the solution.\n\n<details><summary>Step-by-step solution</summary>Four tickets cost 4 × 3 = 12 rupees; add the single fee, 5 + 12 = 17 rupees. The fee is charged once, not per ticket.</details>\n\nCheck your work: identify the quantities, write their units, group where needed, calculate in the shared order, and compare with an estimate. Never round an intermediate exact integer merely because an answer looks awkward.",
        "mistakes": ["Reading every operation strictly left to right changes the expression.", "Multiplying a once-only fee by the number of items confuses the quantities."],
        "items": [numeric("guided-order", "Evaluate 9 - 2 * 3 using conventional arithmetic order. Enter a number, with no unit.", 3, "Multiply 2 by 3 to get 6; subtract 6 from 9 to get 3.", exact_derivation={"op":"subtract","args":["9",{"op":"multiply","args":["2","3"]}]}),
                  numeric("independent-group", "Evaluate (7 + 5) / 3 exactly. Enter a number, with no unit.", 4, "The bracket gives 12; dividing 12 by 3 gives 4.", exact_derivation={"op":"divide","args":[{"op":"add","args":["7","5"]},"3"]}),
                  numeric("transfer-balance", "A prepaid account holds 23 credits. Two bookings each deduct 6 credits; a single refund adds 4 credits. No other changes occur. What balance remains? Enter the number of credits, without a unit.", 15, "Two deductions total 12. The balance is 23 - 12 + 4 = 15 credits.", exact_derivation={"op":"add","args":[{"op":"subtract","args":["23",{"op":"multiply","args":["2","6"]}]},"4"]}),
                  numeric("recall-signed", "A value starts at -4 and increases by 9. What is its final value? Enter a number.", 5, "Move nine units right from -4: -4 + 9 = 5.", exact_derivation={"op":"add","args":["-4","9"]}),
                  numeric("mock-order", "Evaluate 18 / 3 * 2. Multiplication and division have equal precedence. Enter a number.", 12, "Work left to right: 18 / 3 = 6, then 6 * 2 = 12.", exact_derivation={"op":"multiply","args":[{"op":"divide","args":["18","3"]},"2"]})]},
      "logical-reasoning": {
        "intuition": "A pattern question is reliable only when its rule is stated or its assumptions are explicit. A few numbers alone do not determine one inevitable continuation. Separate observing a pattern from applying an agreed rule. A classification is similar: say which property is being tested before deciding which objects belong.",
        "worked": "Suppose the first term is 2 and each following term is exactly 3 greater. The positions and values are 1→2, 2→5, 3→8, 4→11, 5→14. To reach position five, make four additions, not five. This rule is explicit, so its fifth term is uniquely 14. For classification, define the group as whole numbers divisible by 2. Among 6, 9 and 12, only 6 and 12 belong: dividing them by 2 leaves no remainder. That definition says nothing about colour or size.",
        "practice": "Guided: start at 4 and add 2 at every step. The first four values are 4, 6, 8, 10. Independent: the first term is 10 and every next term is 2 smaller. Find the fourth term.\n\n<details><summary>Trace and answer</summary>Position 1 is 10; position 2 is 8; position 3 is 6; position 4 is 4. There are three transitions. No guessing rule is needed.</details>\n\nRevision: write the starting state, state the transition, label positions, enumerate a short trace, and check every supplied value. If no rule is supplied, ask which alternatives are allowed rather than presenting a guess as a mathematical certainty.",
        "mistakes": ["Counting the first term as one transition creates an off-by-one error.", "Several fitted patterns can explain a finite list; a preferred guess is not a uniqueness proof."],
        "items": [numeric("guided-sequence", "The first term is 2. Every following term adds exactly 3. What is term 5? Enter a number.",14,"Enumerate 2, 5, 8, 11, 14; four transitions reach term five.",sequence_proof={"start":2,"step":3,"position":5}),
                  numeric("independent-descending", "Term 1 is 10. Each following term subtracts exactly 2. What is term 4?",4,"The trace is 10, 8, 6, 4.",sequence_proof={"start":10,"step":-2,"position":4}),
                  numeric("transfer-positions", "A marker starts at coordinate -3 at observation 1. Between consecutive observations it moves exactly 4 units right. What coordinate is observed at observation 6?",17,"Five moves add 20 to -3, giving 17. Observation 1 involves no move.",sequence_proof={"start":-3,"step":4,"position":6}),
                  numeric("recall-transition", "Term 1 is 7. Add exactly 5 for each next term. What is term 3?",17,"7, 12, 17 requires two transitions.",sequence_proof={"start":7,"step":5,"position":3}),
                  choice("mock-classify","The classification rule is 'whole numbers divisible by 2'. Which pair both belongs?","6 and 12","6 and 9","Both 6 and 12 have zero remainder on division by 2; 9 does not.")]},
      "verbal-english": {
        "intuition": "A sentence lets a reader connect something being discussed with what happens or is true about it. In a plain statement, look for the subject and its verb before extra detail. A clause contains a subject–verb relationship. An independent clause can stand as a complete statement; a dependent clause relies on surrounding text. These are useful checks for standard edited English, not a judgment about a person's accent or worth.",
        "worked": "In 'Mira checks the report', Mira is the subject, checks is the verb, and the report receives the action. 'Because Mira checks the report' still has a subject and verb, but because makes the thought dependent: the reader expects what follows. 'Because Mira checks the report, errors are found early' connects that reason with an independent clause. Descriptive words can lengthen a sentence without adding another clause. In 'The very small robot moves slowly', the subject is the robot and the verb is moves.",
        "practice": "Guided: in 'The trainees test the app', ask who performs the action (the trainees), then what action occurs (test). Independent: identify the subject and verb in 'A careful reviewer notices mistakes'.\n\n<details><summary>Explanation</summary>The subject is a careful reviewer, with reviewer as its head noun. Notices is the verb. Mistakes is the object, not the subject.</details>\n\nRevision: find the verb, identify its subject, distinguish the object, and ask whether the clause stands alone. Real writing allows several valid formulations. The objective items below ask about specified sentences; open rewrites should be reviewed as reflection, not rejected by matching one model sentence.",
        "mistakes": ["The nearest noun is not automatically the subject.", "A string with a subject and verb can still be a dependent clause."],
        "items": [choice("guided-subject","In the statement 'The courier carries a parcel', which phrase is the subject?","The courier","a parcel","The courier performs the action carries; a parcel receives it."),
                  choice("independent-verb","In 'Our team reviews changes', which word is the verb?","reviews","changes","Reviews describes the action; changes is its object here."),
                  choice("transfer-clause","Which option is an independent clause in standard edited English?","The service restarted.","Although the service restarted","The first is a complete statement. Although makes the second clause dependent."),
                  choice("recall-dependent","In 'Because the build failed, we checked the logs', which clause is dependent?","Because the build failed","we checked the logs","Because marks the reason as dependent on the main statement."),
                  choice("mock-head","In 'The quiet student near the window asks a question', who asks?","The quiet student near the window","the window","The subject is the student phrase; near the window only describes its location.")]},
      "python": {
        "intuition": "Python keeps values such as whole numbers and text. An expression computes a value; assignment gives that value a name. Quotes matter: 6 is an integer, while '6' is text. A name is a label, not a box that permanently remembers an earlier calculation. This lesson uses integers, strings and basic arithmetic only; external packages, files and network access are outside Forge's restricted Submit worker.",
        "worked": "Trace `count = 3`, then `total = count * 4`, then `count = 5`. Total remains 12: assignment evaluated the expression when count was 3. It is not a live spreadsheet formula. Python uses * for multiplication; brackets group operations. The expression `2 + 3 * 4` is 14. The expression `'2' + '3'` joins text into '23', rather than adding numbers. Division / produces a floating-point value; // is floor division. Keep these operations distinct.",
        "practice": "Guided: after `price = 7` and `cost = price + 2`, cost is 9. Independent: compute a total with a fixed fee of 3 plus two times an integer value. For value 4, the result is 11.\n\n<details><summary>Code and explanation</summary>`def solve(value):` names the small function the judge calls; its indented `return 3 + 2 * value` sends the answer back. Return the number, not its printed representation. For value 0, the fee remains 3. The provided function wrapper is only a test interface; complete function design is taught later.</details>\n\nRevision: note types, trace one assignment at a time, use grouping intentionally, preserve the provided function parameters, and test zero and negative inputs when allowed. Run checks public samples; Submit checks additional fixtures.",
        "mistakes": ["Changing a variable later does not retroactively change an already computed value.", "Returning '11' is not the same as returning integer 11."],
        "items": [code("guided-fee","Return the integer 3 + 2 * value for any integer value from -1000 to 1000. Keep solve(value); do not print the answer.","3 + 2 * value",[([4],11),([0],3),([-2],-1)],"Multiply value by 2 before adding the fixed fee of 3."),
                  code("independent-square","Return value * value + 1 for an integer value between -100 and 100. Keep the provided solve(value) signature.","value * value + 1",[([3],10),([0],1),([-4],17)],"The product is computed first. A negative multiplied by itself is nonnegative."),
                  code("transfer-conversion","A sensor reports an integer value in whole minutes, between 0 and 1000. A test event occurs 15 seconds after that many minutes. Return its time in seconds from the origin.","value * 60 + 15",[([2],135),([0],15),([9],555)],"Each minute contributes 60 seconds; add the one-time 15-second offset after conversion."),
                  code("recall-evaluation","Return 10 - 2 * value for an integer between -100 and 100, without converting to text.","10 - 2 * value",[([3],4),([0],10),([-2],14)],"Multiplication is performed before subtraction."),
                  choice("mock-types","What value and type does Python produce for the expression '4' + '5'?","The string '45'","The integer 9","Both operands are strings, so + concatenates them.")]},
      "sql-postgresql": {
        "intuition": "A relational table records one kind of thing in rows; named columns describe it. A primary key identifies a row uniquely and cannot be NULL. A foreign key constrains references to another table: it is not automatically unique. A nullable foreign key may be NULL; NOT NULL is a separate requirement. Think of each library member having one member number, while many loan rows can refer to that number.",
        "worked": "Suppose members has primary key id with rows 2 and 8. Loans has its own primary key id and a nullable member_id referencing members(id). Two loans may both refer to member 2. A loan with member_id 99 is invalid because no member 99 exists. A NULL member_id is allowed unless NOT NULL is added. To inspect existing identifiers, `SELECT id FROM members ORDER BY id` returns 2 then 8. ORDER BY is needed when order matters; storage order is not a result guarantee.",
        "practice": "Guided: distinguish members.id, which identifies a member, from loans.member_id, which refers to one. To find loans without an assigned member use `WHERE member_id IS NULL`; `= NULL` is not that test. Independent: can members with IDs 2 and 8 share the same display name?\n\n<details><summary>Reasoning</summary>Yes, if only id is the primary key and name has no uniqueness constraint. A display name is not necessarily an identifier. Conversely, inserting id 2 twice violates the primary key.</details>\n\nRevision: state what each row represents, find its primary key, describe each reference, consider nullable fields, and state result ordering. Forge Run/Submit use disposable PGlite databases. Learner SQL never runs against Forge history. The coding items inspect supplied schemas; they do not claim to assess unrestricted database administration or live application migrations.",
        "mistakes": ["A foreign key does not imply a one-to-one relationship.", "NULL means missing/unknown, so use IS NULL rather than = NULL."],
        "items": []},
      "dsa": {
        "intuition": "Before choosing an algorithm, agree on what counts as a correct answer. A contract states inputs, outputs, bounds and awkward cases. A trace then follows one small input through the proposed steps. This prevents solving the wrong task quickly. No prior sorting or graph knowledge is needed: our first examples use integer arithmetic and a fully provided function wrapper.",
        "worked": "Define the distance between integer positions a and b as a nonnegative integer. For positions 3 and 8, subtracting gives -5; taking its absolute value gives 5. Reversing the positions still gives 5. Equal positions give 0. In Python, abs(x) returns the magnitude of x, so `return abs(a - b)` matches the contract. Simply returning a - b fails when a is smaller. The work and extra storage are constant for the bounded integers used here; passing these cases is not a proof about arbitrary huge-integer cost.",
        "practice": "Guided: trace a=9, b=4: difference 5, magnitude 5, return integer 5. Independent: state the contract for remaining capacity when used may exceed capacity.\n\n<details><summary>Contract and checked examples</summary>Inputs are two nonnegative integers. Return max(0, capacity - used), never a negative capacity. For capacity 8 and used 3 return 5; for used 11 return 0. Python max(0, difference) chooses the larger value. The exact signature and bounds must be written before submission.</details>\n\nRevision: read the return type, list valid input ranges, trace normal/equal/boundary cases, and construct a counterexample to a tempting wrong method. Hidden tests supplement a clear contract; they cannot rescue an ambiguous statement. Do not print or return a string when an integer is requested.",
        "mistakes": ["A method that works only when a >= b does not implement absolute distance.", "A list, tuple, string and integer are distinct return types in Forge."],
        "items": [code("guided-distance","Return the nonnegative integer distance between positions a and b, each between -1000 and 1000. Keep solve(a, b). Equal positions have distance 0.","abs(a - b)",[([3,8],5),([8,3],5),([4,4],0),([-3,2],5)],"Subtract the positions and take the absolute value.",["a","b"]),
                  code("independent-inclusive","For integers start <= end between -100 and 100, return how many integer positions are in the inclusive interval [start, end]. Keep solve(start, end).","end - start + 1",[([2,4],3),([0,0],1),([-2,1],4)],"The difference counts gaps; add one to count both endpoints.",["start","end"]),
                  code("transfer-ring","Twelve positions labeled 0 through 11 form a ring. One step moves to either adjacent position, with 0 adjacent to 11. Return the fewest steps from a to b, where both inputs are integer labels. Keep solve(a, b).","min(abs(a-b), 12-abs(a-b))",[([1,11],2),([0,11],1),([0,6],6),([4,4],0),([10,2],4)],"Compare the direct distance with the complementary path around the twelve-position ring.",["a","b"]),
                  code("recall-distance","Return the nonnegative integer distance between integer positions a and b in [-1000,1000].","abs(a-b)",[([-4,-1],3),([7,2],5),([0,0],0)],"Absolute difference handles either order and equal positions.",["a","b"]),
                  choice("mock-contract","A function promises a list of two integers. Which result satisfies that return-type contract?","[2, 5]","(2, 5)","The first is a list; the second is a tuple even though its elements match.")]},
      "system-design": {
        "intuition": "Start with the job a small system must do, not a collection of fashionable components. A functional requirement describes a user-visible action. A constraint limits the solution, such as using one school computer. A quality requirement describes a property that can be checked, such as an agreed response-time target under a stated workload. Put the boundary around what this version owns.",
        "worked": "A small club needs a shared equipment notebook. Members can view items and a volunteer can mark an item borrowed or returned. The first version serves 20 members on a local network; payments and public sign-up are out of scope. A simple browser → local service → database path is enough to discuss initially. Before choosing a cache or queue, ask whether a measured problem needs one. If two people request one item at the same moment, the borrowing rule needs an explicit consistency decision; drawing more boxes does not decide it.",
        "practice": "Guided: 'Members can see which items are available' is functional. 'Works on the existing local computer' is a constraint. Independent: define a minimal attendance notebook, list two actions, one limit and one failure case.\n\n<details><summary>Illustrative review, not the only correct design</summary>Record attendance and view a day's list; serve one classroom on the local network; retain a saved record after a restart. Decide whether repeat marks update a record or are rejected. Other coherent boundaries can be valid.</details>\n\nRevision: name the users, state actions, record limits, make success observable, identify failures and exclude tempting extras. Open designs use a rubric; Forge does not automatically judge arbitrary architecture prose.",
        "mistakes": ["A product name such as Redis is a component choice, not a requirement.", "A speed target without workload or measurement conditions is hard to verify."],
        "items": [reflection("guided-boundary","Describe the equipment notebook's users, two functional actions, one constraint and one explicit exclusion.","Members view availability; a volunteer records loans. One local computer is used; payments are excluded.",["Separate user actions from technology choices.","State a boundary and a limitation."]),
                  reflection("independent-attendance","Write a small attendance notebook specification. State a failure case and how success would be checked.","Save one record per learner per date; reject accidental duplicates; verify records survive restart.",["Several coherent answers are possible.","Include an observable check and a failure boundary."])]},
      "ai-fundamentals": {
        "intuition": "AI is a broad label for computer systems performing tasks associated with intelligent behaviour. Machine learning is an approach in which behaviour is fitted from data rather than every rule being hand-written. Deep learning is a family of machine-learning methods using neural networks with multiple learned layers. These are overlapping categories, not three separate products. A system can use ordinary rules without learning from examples.",
        "worked": "Imagine sorting incoming messages. A fixed rule that flags a message when its subject contains a specified word uses no training data. A model fitted to labeled examples of spam and normal messages is machine learning. A multi-layer neural-network classifier is both deep learning and machine learning. Training adjusts learned parameters; inference applies the trained model to a new input. A correct-looking output alone does not establish how the system was built, and a learned model can still make mistakes.",
        "practice": "Guided: a hand-written multiplication function does not become machine learning because it runs on a computer. Independent: a classifier is trained on past labeled messages using a multi-layer neural network. Which categories include it?\n\n<details><summary>Explanation</summary>It is deep learning, which is within machine learning, used for an AI task. The evidence is the stated training method, not a brand name. This tells us nothing by itself about accuracy, fairness or reliability.</details>\n\nRevision: distinguish task, learning method, training and inference; ask what data and evaluation support a claim. These offline scenarios do not require an API key or live model. Product-specific model features change; this lesson deliberately avoids claims about current model prices or capabilities.",
        "mistakes": ["A confident output is not evidence that a model is correct.","Calling every ordinary deterministic program machine learning hides the role of training data."],
        "items": [choice("guided-learning","A message filter's parameters are fitted from labeled examples. Which description follows from that information?","It uses machine learning.","It must use a hand-written rule for every message.","The stated fitting process learns from data; a specific network architecture has not been specified."),
                  choice("independent-inference","A trained classifier is applied to one new message without updating parameters. What stage is this?","Inference","Training","The saved parameters are being used rather than fitted."),
                  choice("transfer-evidence","A team reports that its classifier uses a neural network with several learned layers trained on examples. Which relationship is justified?","It is a deep-learning system and also a machine-learning system.","Deep learning is unrelated to machine learning.","Deep learning is a family of machine-learning methods; the stated architecture supplies the evidence."),
                  choice("recall-fixed-rule","A program always flags a message if the literal word URGENT appears, using only that hand-written rule. What is justified?","This description does not establish machine learning.","Any program reading text must be machine learning.","The description gives no training or learning process."),
                  choice("mock-limits","A model answered one example correctly. What follows?","That one output matched; broader reliability still needs evaluation.","Every future output is guaranteed correct.","One example cannot establish performance across unseen inputs.")]},
      "interview-communication": {
        "intuition": "An introduction helps another person understand what you are doing now and why this conversation is relevant. It is not a competition to invent the strongest biography. Choose a small set of true details: current study or role, one concrete piece of work, what you did, and what you want to learn or contribute. Adapt length to the question and allow the other person to ask more.",
        "worked": "Illustrative rehearsal, not a statement about the learner: 'I am studying computer science. In a small notes project I implemented search and wrote tests for empty results. That taught me to check edge cases. I am interested in an entry-level role where I can strengthen my Python and testing skills.' This gives a current context, a checkable action and a learning direction. It does not claim commercial customers or team leadership. A project description should distinguish your own contribution from the group's work.",
        "practice": "Guided: replace each detail in the example with a true detail of your own; remove any sentence you cannot explain with evidence. Independent: write a short introduction for a placement conversation, then a shorter version for a project discussion.\n\n<details><summary>Self-review questions</summary>Can a listener identify your current context? Is there a specific action you personally took? Have you separated fact from aspiration? Could you explain the project if asked? Is there room for a follow-up? Several clear answers can be equally valid.</details>\n\nRevision: be honest, use concrete actions, avoid unsupported labels, respect the requested length, and ask for clarification when needed. Forge stores this as reflection and supplies a rubric, not an automatic communication score or a prediction of hiring success.",
        "mistakes": ["Invented experience creates claims you cannot support in follow-up questions.","A long list of tools can hide what you personally did."],
        "items": [reflection("guided-introduction","Write a concise, true introduction. Include current context, a concrete personal action and a learning direction.","Illustrative structure: I am studying __. In __ I personally __. I learned __ and want to develop __.",["Use only true personal details.","Explain your own action rather than only naming tools.","Leave space for the interviewer to ask more."]),
                  reflection("independent-project","Adapt your introduction for a project discussion. State one limitation or uncertainty honestly.","I implemented the search screen and tested empty results. I have not yet measured performance on a large corpus.",["Separate your work from team work.","State a limitation without inventing results."])]}
    }


def sql_item(key, prompt, query, transfer=False):
    datasets = [
      {"setup_sql": "CREATE TABLE members(id int PRIMARY KEY); INSERT INTO members VALUES (2),(8); CREATE TABLE loans(id int PRIMARY KEY,member_id int REFERENCES members(id)); INSERT INTO loans VALUES (4,2),(7,NULL),(9,2);", "expected_rows": [[7]] if transfer else [[2],[8]]},
      {"setup_sql": "CREATE TABLE members(id int PRIMARY KEY); INSERT INTO members VALUES (3),(10),(14); CREATE TABLE loans(id int PRIMARY KEY,member_id int REFERENCES members(id)); INSERT INTO loans VALUES (1,NULL),(5,10),(8,NULL);", "expected_rows": [[1],[8]] if transfer else [[3],[10],[14]]},
      {"setup_sql": "CREATE TABLE members(id int PRIMARY KEY); CREATE TABLE loans(id int PRIMARY KEY,member_id int REFERENCES members(id));", "expected_rows": []}]
    return {"key":key,"kind":"sql","prompt":prompt,"explanation":"Inspect the specified key column; use IS NULL for an unassigned optional reference and ORDER BY for deterministic order." if transfer else "Select the primary-key column from members and order by id; do not hard-code the visible values.",
            "contract":{"columns":["id"],"ordered":True,"starter_code":"SELECT ","reference_solution":query,"public_dataset":{"setup_sql":datasets[0]["setup_sql"]},"datasets":datasets,
                        "negative_solutions":["SELECT 2 AS id"]}}


def build():
    sources={s["subject"]:s for s in json.loads((ROOT/"sources.json").read_text(encoding="utf-8"))["sources"]}
    scope=json.loads((REPO_ROOT/"data/placement-foundations-scope.json").read_text(encoding="utf-8"))
    data=authored()
    data["sql-postgresql"]["items"]=[
      sql_item("guided-identifiers","Return every members.id from the supplied members table in increasing id order. The primary key is id; include no other column.","SELECT id FROM members ORDER BY id"),
      choice("independent-foreign-key","Two loan rows reference the same existing members.id. There is no UNIQUE constraint on loans.member_id. Is this permitted by that foreign key?","Yes, the reference alone does not require uniqueness.","No, every foreign-key value must occur only once.","Several loans can reference one member unless another constraint forbids it."),
      sql_item("transfer-unassigned","Loans has its own id and a nullable member_id referencing members(id). Return the IDs of loans that have no assigned member, in increasing loan id order. Do not return member identifiers.","SELECT id FROM loans WHERE member_id IS NULL ORDER BY id",True),
      sql_item("recall-keys","List all primary-key IDs in members in increasing order, including all rows and no extra columns.","SELECT id FROM members ORDER BY id"),
      choice("mock-primary","Which condition is guaranteed by a declared primary key?","Its value identifies each row uniquely and is not NULL.","Its value is always a consecutive positive integer.","Primary keys need not be consecutive or positive; uniqueness and non-nullness are required.")]
    for subject,record in data.items():
        topic=next(t for t in scope["topics"] if t["subject_key"]==subject)
        source=sources[subject]
        provenance={"origin":"original","author":"Forge coding agent — draft author, not a human reviewer",
                    "sources":[{"source_id":source["source_id"],"url":source["url"],"usage":"factual_reference","status":"resolved","upstream_revision":source["upstream_revision"],"notice":"Original Forge prose and questions; no source text/images redistributed. Human factual/coverage review pending."}]}
        items=[]
        for index,raw in enumerate(record["items"]):
            purpose=["practice","practice","transfer","recall","interview"][index]
            if raw["kind"]=="reflection":purpose="practice"
            items.append({**raw,"family":"pf/"+topic["key"]+"/"+raw["key"],"subject":subject,"topic":topic["key"],"level":1,
                          "purposes":[purpose],"independent_variant":purpose=="transfer","hints":["Restate the exact quantities, entities or contract before answering."]})
        exercise={"key":"lesson-reflection","exercise_type":"short_answer","title":"Explain the worked example","prompt_markdown":"Explain the worked example in your own words and identify one mistake to avoid.","difficulty":"learning","hints":[],"content":{"rubric":["Explain the stated steps.","Identify a specific misconception."],"reference_answer":record["mistakes"][0]}}
        sections=[{"slug":slug,"title":title,"order_index":index,"estimated_minutes":8,"learning_objective":topic["learning_outcomes"][0],"markdown":record[field],"examples":[],"key_points":[record["mistakes"][0]],"checkpoint":"Can you explain why each step follows from the stated assumptions?"}
                  for index,(slug,title,field) in enumerate([("intuition","Goal and intuition","intuition"),("worked-example","A worked example and why it works","worked"),("practice-revision","Guided practice, independent practice and revision","practice")])]
        example_checks=[]
        if subject=="python":
            sections[1]["examples"]=[{"language":"python","code":"count = 3\ntotal = count * 4\ncount = 5\nprint(total)","expected_output":"12\n","explanation":"Total stores the value computed before count changes."}]
            example_checks=[{"section_slug":"worked-example","example_index":0,"mode":"python","expected_stdout":"12\n"}]
        if subject=="sql-postgresql":
            sections[1]["examples"]=[{"language":"sql","code":"SELECT id FROM members ORDER BY id","expected_output":json.dumps({"columns":["id"],"rows":[[2],[8]]}),"explanation":"Read supplied member identifiers in an explicit order."}]
            example_checks=[{"section_slug":"worked-example","example_index":0,"mode":"sql","setup_sql":"CREATE TABLE members(id int PRIMARY KEY); INSERT INTO members VALUES (2),(8);","expected_columns":["id"],"expected_rows":[[2],[8]],"order_sensitive":True}]
        lesson={"curriculum_key":"placement-foundations","track_slug":subject,"topic_slug":topic["key"],"title":topic["title"],"description":topic["description"],"version":"1.0.0","learning_objectives":topic["learning_outcomes"],"prerequisites":[],"sections":sections,
                "summary":record["mistakes"],"interview_takeaways":["Explain your reasoning and limits; reading is not mastery."],"common_mistakes":record["mistakes"],"sources":[{"source_id":source["source_id"],"title":source["title"],"url":source["url"],"retrieved_at":STAMP}],"generated_at":STAMP}
        lesson["content_hash"]=digest({k:v for k,v in lesson.items() if k!="generated_at"})
        candidates=[{"content_key":topic["content_key"],"revision":"1.0.0","content_type":"lesson_bundle","payload":{"lesson":lesson,"exercises":[exercise]},"provenance":provenance,"example_checks":example_checks,
                     "coverage":{"key":topic["key"]+"-teaching","version":"1","competencies":[{"id":topic["key"],"status":"covered","lesson_refs":["section/intuition","section/worked-example","section/practice-revision"],"assessment_refs":["exercise/lesson-reflection"]}]}},
                    {"content_key":f"assessment/placement-foundations/{subject}/{topic['key']}","revision":"1.0.0","content_type":"assessment_bundle","payload":{"assessment":{"key":f"assessment/placement-foundations/{subject}/{topic['key']}","version":"1.0.0","items":items}},"provenance":provenance,
                     "coverage":{"key":topic["key"]+"-assessment","version":"1","competencies":[{"id":i["key"],"status":"covered","lesson_refs":["explanation/"+i["key"]],"assessment_refs":["item/"+i["key"]]} for i in items]}}]
        for candidate in candidates:
            suffix="lesson" if candidate["content_type"]=="lesson_bundle" else "assessment"
            path=ROOT/"candidates"/(topic["key"]+"."+suffix+".json")
            path.parent.mkdir(parents=True,exist_ok=True)
            if path.exists():raise ValueError("Refusing to overwrite a review candidate; edit deliberately or use a new revision: "+str(path))
            path.write_text(json.dumps(candidate,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (ROOT/"review-checklist.template.json").write_text(json.dumps({k:False for k in QUALITY_CHECKS},indent=2)+"\n",encoding="utf-8")


def validate():
    paths=sorted((ROOT/"candidates").glob("*.json"));assert len(paths)==18
    for path in paths:
        report=validate_candidate(json.loads(path.read_text(encoding="utf-8")))
        dest=ROOT/"validation"/(path.stem+".validation.json");dest.parent.mkdir(exist_ok=True)
        dest.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        print("valid:",path.name,"— awaiting human review")


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("command",choices=["build","validate"])
    args=parser.parse_args();build() if args.command=="build" else validate()
