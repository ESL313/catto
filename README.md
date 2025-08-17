# Catto

The most "concatenative" concatenative language you've ever seen.

## Hello World

To run a Catto program, you might find Unix's `cat` command particularly helpful.

```
> cat hello_world.cat | catto
Hello World
```

Catto is concatenative because given valid programs `foo.cat` and `bar.cat`, you can concatenate them like so:

```
> cat foo.cat | catto
'foo.cat' was called.
> cat bar.cat | catto
'bar.cat' was called.
> cat foo.cat bar.cat | catto
'foo.cat' was called.
'bar.cat' was called.
```

## Syntax and Semantics

Catto is a concatenative, stack-based language, this means words are evaluated left-to-right.

Every word is a string by default, you can allow whitespace in strings by enclosing them with quotation marks.

```
"strings.cat" $drop
"Catto doesn't actually have comments, '$drop' removes this string from the stack." $drop

foo bar "Hello World" "String with \"nested\" quotes"
```

The program above outputs:

```
> cat strings.cat | catto
foo
bar
Hello World
String with "nested" quotes
```

Like most stack-based languages, Catto has a dictionary that you can store words to. You can define and call words like so:

```
"prefixes.cat" $drop

"The following line stores 'Hello World' to 'My Variable'" $drop
"Hello World" :"My Variable"

"Calling it parses the stored string as a Catto program and runs it." $drop
"Hence 'Hello World' becomes two strings: 'Hello' and 'World'." $drop
$"My Variable"
```

## Factorial

Putting it all together, here's how you might write a program that takes in a number and outputs its factorial:

```
"factorial.cat" $drop

"$dupe $dupe 0 $== $swap 1 $== $or \"$drop 1\" \"$dupe 1 $- $factorial $*\" $if $eval" :factorial
$factorial
```

When running it, you can input your number like so:

```
> cat factorial.cat | catto 5
120
```
