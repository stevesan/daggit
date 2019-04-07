# daggit
## Motivation
This is a little experiment to generate a certain kind of monotoous and error-prone code that I frequently encounter. When writing richly interactive software, such as websites or video games, you often need to keep various pieces of state in sync with each other. For example, keeping GUI objects in sync with the underlying data model, that may be manipulated by different systems (other users, the undo system, etc.). You typically end up with many "update.." functions inside setters, or adopting an event-subscription model. Both can get confusing and tricky to maintain - at least in my experience.

## Experiment
With daggit, I wanted to try generating this code from a declarative specification, like makefiles. So something like:
```
[DependsOn(A,B)]
updateC() {
  someExpensiveComputation();
}
```
This says, "please call updateC whenever A or B change." Then we can generate for you:
```
setA(newA) {
  a = newA;
  updateC();
}

setB(newB) {
  b = newB;
  updateC();
}
```
This kind of code is error-prone to maintain by hand, IMHO, because the definitions of setA and setB are often far from updateC. When updateC changes and its dependencies change, it's not obvious what needs to change. The best place to manage dependencies is near the definition updateC, which is accomplished with the "DependsOn" attribute. (Note: I'm using C#'s attribute syntax, but obviously this is meant to be pseudo-code)

Beyond maintainability, we can also do some common optimizations, like only calling updateC if the values *actually* change:
```
setA(newA) {
  if(a != newA) {
    a = newA;
    updateC();
  }
}
```
Another optimization we can do is, what if user code wants to update both A and B from the same callsite? That would result in updateC getting called twice, wastefully. You really should just set A and B, and then call updateC once, right? With hand-written setters or event subscriptions, I'm not really sure how you cleanly avoid this. But with code generation, we can ask it to explicitly generate a compound setter for A and B. The result would be:
```
setAandB(newA, newB) {
  if(a != newA || b != newB) {
    a = newA;
    b = newB;
    updateC();
  }
}
```
Tada! Now the process of optimizing updates is pretty easy: Just find slow parts, see if a compound setter would be help (ie. you see that redundant updates are the bottleneck), and if so just add one and use it.
