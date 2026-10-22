import json
import os

base_path = r"C:\My PC\git\Forge\content\ai-engineer\v1\python"

def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# --- CONTROL FLOW ---
cf_lesson = {
  "curriculum_key": "default-ai-engineer",
  "track_slug": "python",
  "topic_slug": "control-flow",
  "title": "Control Flow",
  "description": "Learn how to direct the execution path of your programs.",
  "version": "1.0.0",
  "learning_objectives": ["Understand if, elif, else", "Use for and while loops", "Master truthiness and falsiness"],
  "prerequisites": [],
  "sections": [
    {
      "slug": "what-is-control-flow",
      "title": "What is Control Flow?",
      "order_index": 0,
      "estimated_minutes": 2,
      "learning_objective": "Understand the concept of control flow.",
      "markdown": "Control flow is the order in which individual statements, instructions, or function calls are executed or evaluated. By default, scripts execute from top to bottom, but we can change this using control structures.",
      "examples": [],
      "key_points": ["Top to bottom default", "Can branch or loop"]
    },
    {
      "slug": "if-elif-else",
      "title": "If, Elif, and Else",
      "order_index": 1,
      "estimated_minutes": 5,
      "learning_objective": "Use conditional statements.",
      "markdown": "We use if, elif, else to execute code only when certain conditions are met.",
      "examples": [{"language": "python", "code": "x = 5\nif x > 0:\n    print('Positive')\nelif x == 0:\n    print('Zero')\nelse:\n    print('Negative')", "expected_output": "Positive", "explanation": "Branches based on condition"}],
      "key_points": ["Condition evaluation", "Exclusive branching"]
    },
    {
      "slug": "truthiness-and-falsiness",
      "title": "Truthiness and Falsiness",
      "order_index": 2,
      "estimated_minutes": 4,
      "learning_objective": "Understand how Python evaluates boolean contexts.",
      "markdown": "Every object in Python has a boolean value. Some are considered falsiness (like 0, empty lists, None) and others truthiness.",
      "examples": [],
      "key_points": ["Empty is usually false", "Everything else is true"]
    },
    {
      "slug": "for-loops",
      "title": "For Loops",
      "order_index": 3,
      "estimated_minutes": 5,
      "learning_objective": "Iterate over sequences.",
      "markdown": "A for loop is used for iterating over a sequence (that is either a list, a tuple, a dictionary, a set, or a string).",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "while-loops",
      "title": "While Loops",
      "order_index": 4,
      "estimated_minutes": 5,
      "learning_objective": "Loop while a condition is true.",
      "markdown": "A while loop executes a set of statements as long as a condition is true.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "range-function",
      "title": "Range Function",
      "order_index": 5,
      "estimated_minutes": 3,
      "learning_objective": "Generate sequences of numbers.",
      "markdown": "The range function returns a sequence of numbers, starting from 0 by default, and increments by 1.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "break-and-continue",
      "title": "Break and Continue",
      "order_index": 6,
      "estimated_minutes": 3,
      "learning_objective": "Alter loop execution.",
      "markdown": "Use break to exit a loop entirely. Use continue to skip the rest of the current iteration.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "nested-control-flow",
      "title": "Nested Control Flow",
      "order_index": 7,
      "estimated_minutes": 3,
      "learning_objective": "Combine control structures.",
      "markdown": "You can place if statements inside loops, or loops inside other loops.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "match-awareness",
      "title": "Match Awareness",
      "order_index": 8,
      "estimated_minutes": 3,
      "learning_objective": "Know about structural pattern matching.",
      "markdown": "Python 3.10 introduced the match statement for structural pattern matching. Having match awareness is good for newer codebases.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "common-mistakes",
      "title": "Common Mistakes",
      "order_index": 9,
      "estimated_minutes": 2,
      "learning_objective": "Avoid common pitfalls.",
      "markdown": "Off-by-one errors in range, forgetting colons.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "interview-points",
      "title": "Interview Points",
      "order_index": 10,
      "estimated_minutes": 2,
      "learning_objective": "Prepare for interviews.",
      "markdown": "Understanding loop complexities and early exits is crucial.",
      "examples": [],
      "key_points": []
    }
  ],
  "summary": ["Control flow dictates execution", "Loops iterate", "Conditionals branch"],
  "interview_takeaways": ["Know your loop complexities"],
  "common_mistakes": ["Infinite loops"],
  "sources": [
    {"source_id": "python-official-tutorial", "title": "Control Flow Tools", "url": "https://docs.python.org/3/tutorial/controlflow.html", "retrieved_at": "2026-09-23T00:00:00Z"}
  ],
  "content_hash": "fixture-python-control-flow-v1",
  "generated_at": "2026-09-23T00:00:00Z"
}

cf_exercises = [
  {
    "key": "cf-1",
    "exercise_type": "multiple_choice",
    "title": "Truthiness check",
    "prompt_markdown": "What does `bool([])` return?",
    "difficulty": "easy",
    "hints": ["Consider empty collections"],
    "content": {
      "choices": ["True", "False", "None", "Error"],
      "correct_index": 1,
      "explanation": "Empty collections evaluate to False."
    }
  },
  {
    "key": "cf-2",
    "exercise_type": "multiple_choice",
    "title": "Loop iteration",
    "prompt_markdown": "Which statement exits a loop entirely?",
    "difficulty": "easy",
    "hints": ["It 'breaks' the loop"],
    "content": {
      "choices": ["continue", "exit", "break", "pass"],
      "correct_index": 2,
      "explanation": "break exits the current loop."
    }
  },
  {
    "key": "cf-3",
    "exercise_type": "multiple_choice",
    "title": "Range semantics",
    "prompt_markdown": "What does `range(3)` produce?",
    "difficulty": "easy",
    "hints": ["It starts at 0"],
    "content": {
      "choices": ["1,2,3", "0,1,2", "0,1,2,3", "1,2"],
      "correct_index": 1,
      "explanation": "range(n) produces numbers from 0 up to n-1."
    }
  },
  {
    "key": "cf-4",
    "exercise_type": "multiple_choice",
    "title": "Conditional syntax",
    "prompt_markdown": "Which keyword is used for alternative conditions?",
    "difficulty": "easy",
    "hints": ["It's short for else if"],
    "content": {
      "choices": ["elseif", "else if", "elif", "case"],
      "correct_index": 2,
      "explanation": "elif is used in Python."
    }
  },
  {
    "key": "cf-5",
    "exercise_type": "short_answer",
    "title": "Truthiness explanation",
    "prompt_markdown": "Explain the concept of truthiness in Python.",
    "difficulty": "medium",
    "hints": ["Think about non-boolean types"],
    "content": {
      "rubric": ["Mention boolean context", "Mention empty/zero values"],
      "reference_answer": "Truthiness refers to how Python evaluates non-boolean values in a boolean context (like if statements). Empty collections and 0 evaluate to False, others to True.",
      "minimum_pass_score": 70
    }
  },
  {
    "key": "cf-6",
    "exercise_type": "short_answer",
    "title": "Break vs Continue",
    "prompt_markdown": "What is the difference between break and continue?",
    "difficulty": "medium",
    "hints": ["One stops entirely, one skips"],
    "content": {
      "rubric": ["break stops the loop", "continue skips to next iteration"],
      "reference_answer": "break exits the loop entirely, while continue skips the remainder of the current iteration and proceeds to the next iteration.",
      "minimum_pass_score": 70
    }
  }
]

# --- STRINGS ---
str_lesson = {
  "curriculum_key": "default-ai-engineer",
  "track_slug": "python",
  "topic_slug": "strings",
  "title": "Strings",
  "description": "Learn to manipulate text in Python.",
  "version": "1.0.0",
  "learning_objectives": ["Understand immutability", "Master string methods", "Use f-strings"],
  "prerequisites": [],
  "sections": [
    {
      "slug": "what-is-a-string",
      "title": "What is a String?",
      "order_index": 0,
      "estimated_minutes": 2,
      "learning_objective": "Understand text representation.",
      "markdown": "A string is a sequence of characters. In Python, they are enclosed in quotes.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "indexing-and-slicing",
      "title": "Indexing and Slicing",
      "order_index": 1,
      "estimated_minutes": 4,
      "learning_objective": "Access parts of a string.",
      "markdown": "Strings support indexing (accessing single characters) and slicing (extracting substrings).",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "immutability",
      "title": "Immutability",
      "order_index": 2,
      "estimated_minutes": 3,
      "learning_objective": "Understand that strings cannot be changed.",
      "markdown": "Strings are immutable, meaning once created, they cannot be modified in place.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "string-methods",
      "title": "String Methods",
      "order_index": 3,
      "estimated_minutes": 5,
      "learning_objective": "Use built-in methods.",
      "markdown": "Python provides many useful methods for transforming strings.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "strip-split-join",
      "title": "Strip, Split, Join",
      "order_index": 4,
      "estimated_minutes": 5,
      "learning_objective": "Clean and combine strings.",
      "markdown": "Use strip to remove whitespace, split to break into a list, and join to combine a list into a string.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "replace-find-in",
      "title": "Replace, Find, In",
      "order_index": 5,
      "estimated_minutes": 4,
      "learning_objective": "Search and modify.",
      "markdown": "Use replace to swap substrings, find to locate index, and 'in' for membership.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "f-strings-and-formatting",
      "title": "F-strings and Formatting",
      "order_index": 6,
      "estimated_minutes": 4,
      "learning_objective": "Format text dynamically.",
      "markdown": "An f-string allows embedding expressions directly into string literals, replacing older formatting methods.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "reverse-and-palindrome",
      "title": "Reverse and Palindrome",
      "order_index": 7,
      "estimated_minutes": 3,
      "learning_objective": "Common string operations.",
      "markdown": "Reversing a string is easily done with slicing [::-1]. A palindrome reads the same forwards and backwards.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "anagram-pattern",
      "title": "Anagram Pattern",
      "order_index": 8,
      "estimated_minutes": 4,
      "learning_objective": "Solve anagram problems.",
      "markdown": "An anagram is formed by rearranging letters. Often solved by sorting or using character counts.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "common-mistakes",
      "title": "Common Mistakes",
      "order_index": 9,
      "estimated_minutes": 2,
      "learning_objective": "Avoid pitfalls.",
      "markdown": "Forgetting that string methods return new strings rather than mutating.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "interview-points",
      "title": "Interview Points",
      "order_index": 10,
      "estimated_minutes": 2,
      "learning_objective": "Nail the interview.",
      "markdown": "Be ready to implement a palindrome check, solve anagrams, or reverse strings in an interview setting.",
      "examples": [],
      "key_points": []
    }
  ],
  "summary": ["Strings are text data", "They are immutable"],
  "interview_takeaways": ["String algorithms are very common"],
  "common_mistakes": ["Mutating strings"],
  "sources": [
    {"source_id": "python-official-tutorial", "title": "Text Sequence Type - str", "url": "https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str", "retrieved_at": "2026-09-23T00:00:00Z"}
  ],
  "content_hash": "fixture-python-strings-v1",
  "generated_at": "2026-09-23T00:00:00Z"
}

str_exercises = [
  {
    "key": "str-1",
    "exercise_type": "multiple_choice",
    "title": "Slicing",
    "prompt_markdown": "What does `\"hello\"[1:3]` return?",
    "difficulty": "easy",
    "hints": ["It is 0-indexed"],
    "content": {
      "choices": ["he", "el", "ell", "lo"],
      "correct_index": 1,
      "explanation": "Indices 1 up to but not including 3 are 'e' and 'l'."
    }
  },
  {
    "key": "str-2",
    "exercise_type": "multiple_choice",
    "title": "Immutability",
    "prompt_markdown": "Can you change a character in a string via `s[0] = 'a'`?",
    "difficulty": "easy",
    "hints": ["Strings are immutable"],
    "content": {
      "choices": ["Yes", "No", "Sometimes", "Only in Python 3"],
      "correct_index": 1,
      "explanation": "No, strings are immutable."
    }
  },
  {
    "key": "str-3",
    "exercise_type": "multiple_choice",
    "title": "String Methods",
    "prompt_markdown": "Which method splits a string into a list?",
    "difficulty": "easy",
    "hints": ["It divides it"],
    "content": {
      "choices": ["divide()", "partition()", "split()", "break()"],
      "correct_index": 2,
      "explanation": "split() is the standard method."
    }
  },
  {
    "key": "str-4",
    "exercise_type": "multiple_choice",
    "title": "F-strings",
    "prompt_markdown": "How do you start an f-string?",
    "difficulty": "easy",
    "hints": ["It's a prefix"],
    "content": {
      "choices": ["$''", "f''", "format''", "''f"],
      "correct_index": 1,
      "explanation": "Prefix the string with 'f' or 'F'."
    }
  },
  {
    "key": "str-5",
    "exercise_type": "short_answer",
    "title": "String Reversal",
    "prompt_markdown": "How do you reverse a string `s` in Python cleanly using slicing?",
    "difficulty": "medium",
    "hints": ["Step size of -1"],
    "content": {
      "rubric": ["Use slicing", "[::-1]"],
      "reference_answer": "You can use `s[::-1]`.",
      "minimum_pass_score": 70
    }
  },
  {
    "key": "str-6",
    "exercise_type": "short_answer",
    "title": "Join explained",
    "prompt_markdown": "Explain how the `join()` method works on strings.",
    "difficulty": "medium",
    "hints": ["It's called on the separator"],
    "content": {
      "rubric": ["Called on separator string", "Takes iterable of strings"],
      "reference_answer": "`join()` is called on a separator string and takes an iterable of strings, concatenating them with the separator in between.",
      "minimum_pass_score": 70
    }
  }
]

# --- COLLECTIONS ---
col_lesson = {
  "curriculum_key": "default-ai-engineer",
  "track_slug": "python",
  "topic_slug": "collections",
  "title": "Collections",
  "description": "Learn lists, tuples, sets, and dicts.",
  "version": "1.0.0",
  "learning_objectives": ["Understand core structures", "Know selection trade-offs", "Perform iterations and mutations"],
  "prerequisites": [],
  "sections": [
    {
      "slug": "which-collection-when",
      "title": "Which Collection When",
      "order_index": 0,
      "estimated_minutes": 3,
      "learning_objective": "Choose the right structure.",
      "markdown": "Python has lists, tuples, dictionaries, and sets. Pick the right tool for the job.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "lists-basics",
      "title": "Lists Basics",
      "order_index": 1,
      "estimated_minutes": 3,
      "learning_objective": "Use lists.",
      "markdown": "Lists are ordered, mutable sequences, supporting indexing and slicing.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "list-mutation",
      "title": "List Mutation",
      "order_index": 2,
      "estimated_minutes": 3,
      "learning_objective": "Modify lists.",
      "markdown": "Lists support mutation like append, extend, insert, pop, remove.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "list-slicing-copying",
      "title": "List Slicing and Copying",
      "order_index": 3,
      "estimated_minutes": 3,
      "learning_objective": "Slice lists.",
      "markdown": "Slicing allows you to extract sub-lists. Remember it creates a shallow copy.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "tuples-basics",
      "title": "Tuples Basics",
      "order_index": 4,
      "estimated_minutes": 3,
      "learning_objective": "Use tuples.",
      "markdown": "Tuples are ordered and immutable. Great for fixed collections.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "tuple-packing-unpacking",
      "title": "Tuple Packing and Unpacking",
      "order_index": 5,
      "estimated_minutes": 3,
      "learning_objective": "Pack/unpack variables.",
      "markdown": "Assigning multiple values packs them into a tuple; you can also unpack them into multiple variables.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "sets-basics",
      "title": "Sets Basics",
      "order_index": 6,
      "estimated_minutes": 3,
      "learning_objective": "Use sets.",
      "markdown": "Sets are unordered collections of unique elements. Fast membership testing.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "set-operations",
      "title": "Set Operations",
      "order_index": 7,
      "estimated_minutes": 3,
      "learning_objective": "Perform set math.",
      "markdown": "Union, intersection, difference, symmetric difference.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "dict-basics",
      "title": "Dict Basics",
      "order_index": 8,
      "estimated_minutes": 3,
      "learning_objective": "Use dictionaries.",
      "markdown": "Dictionaries are key-value mappings. Fast lookups.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "dict-access-methods",
      "title": "Dict Access Methods",
      "order_index": 9,
      "estimated_minutes": 3,
      "learning_objective": "Access dict data.",
      "markdown": "Use keys(), values(), items(), and get().",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "dict-iteration",
      "title": "Dict Iteration",
      "order_index": 10,
      "estimated_minutes": 3,
      "learning_objective": "Iterate over dicts.",
      "markdown": "Standard iteration over a dict yields its keys.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "nested-collections",
      "title": "Nested Collections",
      "order_index": 11,
      "estimated_minutes": 3,
      "learning_objective": "Combine structures.",
      "markdown": "Lists of dicts, dicts of lists.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "common-mistakes",
      "title": "Common Mistakes",
      "order_index": 12,
      "estimated_minutes": 3,
      "learning_objective": "Avoid common traps.",
      "markdown": "Modifying while iterating, mutable default arguments.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "selection-trade-offs",
      "title": "Selection Trade-offs",
      "order_index": 13,
      "estimated_minutes": 3,
      "learning_objective": "Performance implications.",
      "markdown": "List vs set lookup time (O(n) vs O(1)). Choose wisely.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "interview-points",
      "title": "Interview Points",
      "order_index": 14,
      "estimated_minutes": 3,
      "learning_objective": "Acing the interview.",
      "markdown": "Always use a set/dict for O(1) membership checks.",
      "examples": [],
      "key_points": []
    }
  ],
  "summary": ["Four core structures", "Lists are mutable", "Sets/Dicts are fast"],
  "interview_takeaways": ["Use dicts for caching/lookups"],
  "common_mistakes": ["Modifying collection while iterating"],
  "sources": [
    {"source_id": "python-official-tutorial", "title": "Data Structures", "url": "https://docs.python.org/3/tutorial/datastructures.html", "retrieved_at": "2026-09-23T00:00:00Z"}
  ],
  "content_hash": "fixture-python-collections-v1",
  "generated_at": "2026-09-23T00:00:00Z"
}

col_exercises = [
  {
    "key": "col-1",
    "exercise_type": "multiple_choice",
    "title": "Dict additions",
    "prompt_markdown": "Which is the correct way to add a key to a dict `d`?",
    "difficulty": "easy",
    "hints": ["Use assignment"],
    "content": {
      "choices": ["d.add('k', 'v')", "d.insert('k', 'v')", "d['k'] = 'v'", "d.append('k', 'v')"],
      "correct_index": 2,
      "explanation": "Assignment via index syntax adds or updates a key."
    }
  },
  {
    "key": "col-2",
    "exercise_type": "multiple_choice",
    "title": "Set features",
    "prompt_markdown": "Which of the following is true about sets?",
    "difficulty": "easy",
    "hints": ["Duplicates?"],
    "content": {
      "choices": ["They maintain order", "They allow duplicates", "Elements must be hashable", "They are immutable"],
      "correct_index": 2,
      "explanation": "Sets only store hashable (immutable) elements to ensure uniqueness."
    }
  },
  {
    "key": "col-3",
    "exercise_type": "multiple_choice",
    "title": "List vs Tuple",
    "prompt_markdown": "What is a key difference between lists and tuples?",
    "difficulty": "easy",
    "hints": ["Mutability"],
    "content": {
      "choices": ["Lists are immutable", "Tuples are immutable", "Tuples use brackets []", "Lists cannot be nested"],
      "correct_index": 1,
      "explanation": "Tuples cannot be changed once created."
    }
  },
  {
    "key": "col-4",
    "exercise_type": "multiple_choice",
    "title": "Dict fetching",
    "prompt_markdown": "Which method avoids a KeyError if a key is missing?",
    "difficulty": "easy",
    "hints": ["It 'gets' it safely"],
    "content": {
      "choices": ["d.fetch(k)", "d[k]", "d.get(k)", "d.has(k)"],
      "correct_index": 2,
      "explanation": "get() returns None instead of raising an error."
    }
  },
  {
    "key": "col-5",
    "exercise_type": "short_answer",
    "title": "Tuples as keys",
    "prompt_markdown": "Explain why tuples are preferred over lists as dictionary keys.",
    "difficulty": "medium",
    "hints": ["Hashability"],
    "content": {
      "rubric": ["Tuples are immutable", "Lists are not hashable"],
      "reference_answer": "Dictionary keys must be hashable. Tuples are immutable and therefore hashable, whereas lists are mutable and cannot be used as keys.",
      "minimum_pass_score": 70
    }
  },
  {
    "key": "col-6",
    "exercise_type": "short_answer",
    "title": "Set vs List",
    "prompt_markdown": "When should you use a set instead of a list?",
    "difficulty": "medium",
    "hints": ["Uniqueness and lookup speed"],
    "content": {
      "rubric": ["Fast lookups", "Unique elements"],
      "reference_answer": "Use a set when you need to ensure elements are unique, or when you need fast O(1) membership testing.",
      "minimum_pass_score": 70
    }
  }
]

# --- FUNCTIONS ---
fn_lesson = {
  "curriculum_key": "default-ai-engineer",
  "track_slug": "python",
  "topic_slug": "functions",
  "title": "Functions",
  "description": "Learn to write reusable code blocks.",
  "version": "1.0.0",
  "learning_objectives": ["Define functions", "Understand scope", "Master arguments and kwargs"],
  "prerequisites": [],
  "sections": [
    {
      "slug": "what-is-a-function",
      "title": "What is a Function?",
      "order_index": 0,
      "estimated_minutes": 2,
      "learning_objective": "Understand function purpose.",
      "markdown": "A function is a block of code which only runs when it is called. You can pass data into a function.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "defining-and-calling",
      "title": "Defining and Calling",
      "order_index": 1,
      "estimated_minutes": 3,
      "learning_objective": "Basic function definition.",
      "markdown": "Use the def keyword to create a function, and parenthesis to call it.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "parameters-and-arguments",
      "title": "Parameters and Arguments",
      "order_index": 2,
      "estimated_minutes": 3,
      "learning_objective": "Pass data.",
      "markdown": "Parameters are defined in the signature; arguments are the actual values passed.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "return-values",
      "title": "Return Values",
      "order_index": 3,
      "estimated_minutes": 3,
      "learning_objective": "Return results.",
      "markdown": "Use the return statement to send data back to the caller.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "default-arguments",
      "title": "Default Arguments",
      "order_index": 4,
      "estimated_minutes": 3,
      "learning_objective": "Set defaults.",
      "markdown": "You can assign default values to parameters. Warning: avoid mutable defaults like lists.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "keyword-arguments",
      "title": "Keyword Arguments",
      "order_index": 5,
      "estimated_minutes": 3,
      "learning_objective": "Pass by name.",
      "markdown": "You can send arguments with the key=value syntax, ignoring order.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "args-and-kwargs",
      "title": "Args and Kwargs",
      "order_index": 6,
      "estimated_minutes": 4,
      "learning_objective": "Variable arguments.",
      "markdown": "Use *args for variable positional arguments, and **kwargs for variable keyword arguments.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "scope-and-legb",
      "title": "Scope and LEGB",
      "order_index": 7,
      "estimated_minutes": 4,
      "learning_objective": "Understand scope.",
      "markdown": "Variable scope follows the LEGB rule: Local, Enclosing, Global, Built-in.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "pure-functions",
      "title": "Pure Functions",
      "order_index": 8,
      "estimated_minutes": 3,
      "learning_objective": "Write side-effect free code.",
      "markdown": "Pure functions always produce the same output for the same input and have no side effects.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "lambda",
      "title": "Lambda",
      "order_index": 9,
      "estimated_minutes": 3,
      "learning_objective": "Anonymous functions.",
      "markdown": "Small anonymous functions defined with the lambda keyword.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "first-class-functions",
      "title": "First-Class Functions",
      "order_index": 10,
      "estimated_minutes": 3,
      "learning_objective": "Functions as objects.",
      "markdown": "Functions can be passed as arguments or returned from other functions.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "common-mistakes",
      "title": "Common Mistakes",
      "order_index": 11,
      "estimated_minutes": 2,
      "learning_objective": "Avoid pitfalls.",
      "markdown": "Mutable default arguments are the most common pitfall.",
      "examples": [],
      "key_points": []
    },
    {
      "slug": "interview-points",
      "title": "Interview Points",
      "order_index": 12,
      "estimated_minutes": 2,
      "learning_objective": "Nail the interview.",
      "markdown": "Expect questions on decorators or closure scope.",
      "examples": [],
      "key_points": []
    }
  ],
  "summary": ["Functions encapsulate logic", "Watch out for mutable defaults"],
  "interview_takeaways": ["Understand LEGB scope rule"],
  "common_mistakes": ["def foo(l=[]):"],
  "sources": [
    {"source_id": "python-official-tutorial", "title": "Defining Functions", "url": "https://docs.python.org/3/tutorial/controlflow.html#defining-functions", "retrieved_at": "2026-09-23T00:00:00Z"}
  ],
  "content_hash": "fixture-python-functions-v1",
  "generated_at": "2026-09-23T00:00:00Z"
}

fn_exercises = [
  {
    "key": "fn-1",
    "exercise_type": "multiple_choice",
    "title": "Variable positional args",
    "prompt_markdown": "Which syntax is used for variable length positional arguments?",
    "difficulty": "easy",
    "hints": ["It uses a single asterisk"],
    "content": {
      "choices": ["**kwargs", "*args", "args[]", "...args"],
      "correct_index": 1,
      "explanation": "*args packs remaining positional arguments into a tuple."
    }
  },
  {
    "key": "fn-2",
    "exercise_type": "multiple_choice",
    "title": "Return defaults",
    "prompt_markdown": "What does a Python function return if there is no return statement?",
    "difficulty": "easy",
    "hints": ["It doesn't return nothing, but it returns..."],
    "content": {
      "choices": ["0", "False", "None", "Error"],
      "correct_index": 2,
      "explanation": "Functions without an explicit return statement return None."
    }
  },
  {
    "key": "fn-3",
    "exercise_type": "multiple_choice",
    "title": "Lambda syntax",
    "prompt_markdown": "How do you define a lambda function that adds 1 to x?",
    "difficulty": "easy",
    "hints": ["Use the lambda keyword"],
    "content": {
      "choices": ["lambda x: x + 1", "lambda(x) { x + 1 }", "def lambda(x): return x + 1", "lambda x => x + 1"],
      "correct_index": 0,
      "explanation": "The syntax is lambda arguments: expression."
    }
  },
  {
    "key": "fn-4",
    "exercise_type": "multiple_choice",
    "title": "Scope acronym",
    "prompt_markdown": "What does LEGB stand for in Python scope resolution?",
    "difficulty": "easy",
    "hints": ["Local is first"],
    "content": {
      "choices": ["Local, Enclosing, Global, Built-in", "Logical, External, Global, Base", "Local, External, Global, Built-in", "List, Enum, Global, Boolean"],
      "correct_index": 0,
      "explanation": "It dictates the order Python resolves variable names."
    }
  },
  {
    "key": "fn-5",
    "exercise_type": "short_answer",
    "title": "Mutable Defaults",
    "prompt_markdown": "Why is it dangerous to use a mutable object like a list as a default argument value?",
    "difficulty": "medium",
    "hints": ["It evaluates only once"],
    "content": {
      "rubric": ["Evaluated once at definition time", "Shared across calls"],
      "reference_answer": "Default arguments are evaluated only once at function definition time. If a mutable object is used, the same object is shared across all calls that use the default, leading to unexpected behavior.",
      "minimum_pass_score": 70
    }
  },
  {
    "key": "fn-6",
    "exercise_type": "short_answer",
    "title": "Pure functions",
    "prompt_markdown": "What defines a 'pure function'?",
    "difficulty": "medium",
    "hints": ["Side effects"],
    "content": {
      "rubric": ["No side effects", "Same output for same input"],
      "reference_answer": "A pure function always returns the same output for the same input and has no observable side effects (like modifying global state or performing I/O).",
      "minimum_pass_score": 70
    }
  }
]


# Writing all to disk
topics = {
  "control-flow": (cf_lesson, cf_exercises),
  "strings": (str_lesson, str_exercises),
  "collections": (col_lesson, col_exercises),
  "functions": (fn_lesson, fn_exercises)
}

for topic, (lesson, exercises) in topics.items():
    topic_dir = os.path.join(base_path, topic)
    write_json(os.path.join(topic_dir, "lesson.json"), lesson)
    write_json(os.path.join(topic_dir, "exercises.json"), exercises)

print("SUCCESS")
