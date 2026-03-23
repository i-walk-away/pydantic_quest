## Where Pydantic belongs

Let's continue using the same website example from the previous lesson.
The user enters two values:

```text
Enter your username: ...
Enter your age: ...
```

Then our app uses this data to calculate how old they will be next year.

You might recall the path that this data takes through our application:

1. User sends `username` and `age`
2. We build a `UserFormDTO` out of this data
3. We call `calculate_age` function and pass the DTO as an argument to it
4. The age is calculated
5. The result is returned to the user

Now let's zoom in on what is actually happening here.

One part of our code receives raw, volatile data from the outside world. That data may be wrong, incomplete, malformed,
or just silly.

Another part of our code does the actual work (calculates `age + 1`)

Smart people from the software architecture field had came up with names for these two parts:

- the part that receives input from the outside world is often called the **API layer** or **presentation layer**
- the part that does the actual work is often called the **business logic layer**

An analogy will make the separation of concerns easier to understand.

Imagine a wooden gate. There is a guard standing in front of it - **Sir API Layer**. Behind the gate, there is a big room
full of machines that do different things. There is an age calculating machine, username changing machine and a whole lot
of others. This room is the **business logic layer**.

So a man approaches the gate with a request: "what age will i be next year?". He writes
down his age and name on a piece of paper and hands it to **Sir API Layer**. It is then the _guards_
responsibility to make sure that the data is valid before he goes into the **business logic layer** and
feeds the data into the age calculating machine. The output is then received by the guard and handed out to the user.

The busiess logic layer is nothing but a collection of functions that do different things. The presentation layer is
just a user-facing interface that accepts requests and knows which functions to call.

They have their own respective responsibilities. For example, as we established in the previous lesson, data validation
is better handled *before* it reaches the actual machines - in the **API layer**.

In an ideal world, these two layers are so isolated from each other that, as long as the _contract_ between them remains
unchanged, one layer can be _heavily_ rewritten without forcing ANY changes in the other. Here, _contract_ means the
agreed shape of the input and output between the two layers: what fields the input DTOs have, and what data is returned.

## Assignment

Open the `Questions` tab in the practice panel on the right and complete the quiz.
