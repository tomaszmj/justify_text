Simple program that justifies given text. Program requires one argument (line length) and reads text from standard input. Usage example:
```
cat testdata/lorem_ipsum.txt | python3 justify.py 35
```
Text justification algorithm minimizes custom "badness" function (defined as sum of squares of all additional spaces) using dynamic programming.

This is loosely inspired by [a lecture from MIT OpenCourseWare](https://www.youtube.com/watch?v=ENyox7kNKeY).
