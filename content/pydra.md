Title: Counting down from infinity, and other tricks with __del__ 
Date: 2014-03-24 01:00
Category: Programming 
Tags: coding, hacker school, python
Slug: here-there-be-pydras
Author: Andree Monette
Summary: Today, I solved 8-queens in Python's garbage collector, along with ...

Today, I solved 8-queens in Python's garbage collector, along with other horrific abuses of same. Python provides the [rather](http://stackoverflow.com/questions/3554952/del-at-program-end) [controversial](http://stackoverflow.com/questions/10352480/how-to-use-del-in-a-reliable-way) magic method `__del__`, which (might!) be called before an object is garbage collected. Playing with this (in CPython 2.7.3) yields some amusing results.

First, there's figuring out where `__del__` even gets called. I wrote a [script to illustrate some common cases](http://github.com/andreecmonette/pydras/blob/master/omnom.py) -- Python uses [reference counting](http://en.wikipedia.org/wiki/Reference_counting) with explicit collection of cycles. That is, for each object that exists, Python keeps an count of the number of times that variable is referred to, such as if it gets assigned explicitly to a variable name, included in an array, assigned as an attribute of some other object, and so on. Whenever a variable name passes out of scope or some containing object is garbage collected, the reference counter for that object is decremented. Once it hits 0, Python (usually, we'll see an exception soon) garbage collects the object, calling the `__del__` method and freeing up its memory. Python also attempts to clear cyclic references, such as in the following example:
    
    :::python
    a = Omnom()
    a.b = Omnom()
    a.b.c = a

It notably won't do so if they have user-defined `__del__` methods, as it doesn't know what order is safe to execute those methods in.

The details of garbage collection are implementation-specific, so there are differences in how this is handled between the default CPython and other implementations. There are also interesting consequences from, for example, being in a REPL - whatever was returned to the terminal last ends up in the `_` variable, so it counts as a reference and the object isn't garbage collected immediately.

--------

So how do we abuse this? Well, we can write [a program that counts backwards from "infinity"](http://github.com/andreecmonette/pydras/blob/master/countdown.py):

    :::python
    class Countdown:
      def __del__(self):
        Countdown().count = self.count + 1
        print self.count
    Countdown().count = 5

This produces:

    Exception RuntimeError: 'maximum recursion depth exceeded while calling a Python object' in <bound method Countdown.__del__ of <__main__.Countdown instance at 0x7f570b3ea878>> ignored
    336
    335
    334
    333
    ...
    9
    8
    7
    6
    5

In this case, `Countdown()` instances are generated until the recursion limit is reached. This doesn't halt program execution because `__del__` explicitly ignores exceptions, but still short-circuits the function call and the instantiations end. They are then resolved in reverse order (actually, outwards from the innermost object).

--------

Another trick that we can do is to create a mythological beast of old, spawning two instances for each deleted instance. Enter [the Pydra](http://github.com/andreecmonette/pydras/blob/master/pydra.py):

    :::python
    class Pydra:
      def __init__(self, neck):
        self.neck = neck
      def __del__(self):
        print self.neck
        Pydra(self.neck + "l")
        Pydra(self.neck + "r")
    
    Pydra("")

As the beast's heads are cut off, two immediately grow back from the severed stump - at least until the recursion limit is hit. What do we get from this? Setting the recursion limit to a reasonably low number with an inserted call of `sys.setrecursionlimit(16)` and suppressing the ignored recursion limit exceptions shows nicely what's going on:

    $ python pydra.py 2>/dev/null
    
    l
    ll
    lll
    llr
    lr
    lrl
    lrr
    r
    rl
    rll
    rlr
    rr
    rrl
    rrr

The garbage collector executes a [depth-first search](http://en.wikipedia.org/wiki/Depth-first_search)! Other tree traversals are possible as well - breadth-first search, for example, is possible by defining a `__del__` method in [a container class](https://github.com/andreecmonette/pydras/blob/master/shyPydra.py).

By making a very small change to this program, it's possible to create an unbounded memory leak. The [Learnean Pydra](http://github.com/andreecmonette/pydras/blob/master/learneanPydra.py) assigns the two created objects to local variables. This causes the call stack pointer to be incremented as the tree deepens. Once this pointer reaches 50 (which is defined in the CPython source in [includes/object.h](https://github.com/python-git/python/blob/master/Include/object.h) as PyTrash_UNWIND_LEVEL) it's added to a trashcan stack for deallocation later. This also causes the tree traversal to terminate at 50 and unwind, doing a [pleasant looking depth-first search](/images/fractalDFS.png). Since the deallocator continues to get called on objects when the call stack is longer than 50, it keeps allocating more memory onto the heap with the `mmap()` and `brk()` system calls ([thanks, strace!](http://jvns.ca/blog/2013/12/22/fun-with-strace/)) until the kernel panics. Without the delay introduced by `print`ing the output, this can fill all the memory up in a typical laptop within a few seconds. By contrast, the Pydra never allocates additional memory at all, and in fact makes no system calls besides `write()` to spit output (and ignored errors) to stdout and stderr.

--------

Finally, I decided to cap off all this `__del__` nonsense by implementing an 8-queens solver using the tree traversal we get for free using the garbage collector. The result is [delqueen](https://github.com/andreecmonette/pydras/blob/master/delqueen.py), a standalone or [importable](https://github.com/andreecmonette/pydras/blob/master/importqueens.py) module that defines a class method and assigns an object representing an empty board. Then it loops until the user terminates the program with `SIGINT`/`^C`, at which point the board is garbage collected. Upon collection, a board checks to see if it's an illegal position or a solution (incrementing a solution counter crudely slapped on the `__builtins__` module, because if we've abused Python this far, might as well take it all the way). If it isn't, it spawns 8 instances of its own class with queens added to the following row. To add to the absurdity, this is in fact an N-queens solver, with N being the length of `__name__`. (Unless explicitly set by an importing file, this is either `'__main__'` or `'delqueen'`, which are incidentally 8 characters long.)

The results should be, at the very least, informative:

    $ python delqueen.py
    Interrupt me!
    ^CTraceback (most recent call last):
      File "delqueen.py", line 39, in <module>
          while True:
            KeyboardInterrupt
            15720 board states traversed.
            The number of 8-queens solutions is: 92
