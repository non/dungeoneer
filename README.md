## Dungeoneer

Dungeoneer is a Python 2 module designed to parse ad-hoc dungeon grids. Simple
games that are grid-based can encode levels (or templates) in a simple,
easy-to-read text format and then parse them using this module.

### Getting Started

You can run the parser on an example file via:

```
$ ./test doc/example
```

### Design

Input data should be in the following format:

```
kobold throne room
#######
#.$K$.#
#.g,g.#
#.k,k.#
#.k,k.#
###+###
#:terrain="wall"
K:creature="kobold king",terrain="throne"
g:creature="kobold guard"
k:creature="kobold"
+:terrain="door"
$:item="chest"
,:terrain="carpet"
```

There are three sections to the data: the name, the map, and the key. The name
shoudl be fairly self-explanatory. The map is the actual grid of coordinates
and attributes. The key maps each map square (a single ASCII character) to a
dictionary of attributes.

Two map square types are built-in: `.` and ` ` (dot and space). These squares
have no attributes, and cannot be overridden in the key.

For now, attribute values can only be (double-quoted) strings, although in the
future the module may be extended to support other types of values. For
instance, each value might be a JSON value to allow arbitrary nesting.

### Using The Module

The `Parser` will parse the file, and then call methods on the user-provided
`Builder` instance. This could populate a level in a game, add to an existing
level, or anything else.

Users are expected to subclass `Builder` and implement three methods:

 * `prepare(name, width, height)`: This method is called once before anything else, and should perform any required setup (e.g. allocating a map). The `width` and `height` are determined from the map.
 * `place(x, y, c, attrs)`: This method is called once for each square in the provided map. The `x` and `y` are relative coordinates of the square, `c` is the ASCII character used in the map, and `attrs` is a dictionary mapping strings to strings.
 * `finalize()`: This method is called once at the very end. Any kind of calculations that should only be performed when all squares have been placed should be done here.

The `TestBuilder` which is provided will simply build and return a string
representation of the given map. It's mostly useful for testing whether data
files are valid or not.
