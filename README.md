# PLY Protobuf

[Protocol Buffers] [0] lexer &amp; parser written in Python for [PLY] [1].

With this library you can create and process parse trees of a Protocol Buffers files with Python. For example usage see `demo.py`.

## Dependency
* This project has only one dependency, [PLY] [1].
* ply/ subdirectory is present in this repo just for demonstration purposes only. If you intend to use this, prefer better original
 [PLY] [1] repository which is up-to-date.
 
## Contributions
* This is my first PLY / parser generator project, there may be bugs although it works for me for quite complicated protocol buffers files. 
If you find a bug, please feel free to submit a pull request or file an issue.

## Acknowledgement
This work was inspired by:
* [plyj] [2], Java lexer &amp; parser for PLY.
* [pyparsing] [3], Protocol Buffers parsing example. 
 
 [0]: https://developers.google.com/protocol-buffers/
 [1]: https://github.com/dabeaz/ply
 [2]: https://github.com/musiKk/plyj
 [3]: http://pyparsing.wikispaces.com/