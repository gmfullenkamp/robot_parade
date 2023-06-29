#!/bin/bash
find . -type f -name "*.py" | xargs pylint --output-format=text | tee pylint.txt
score=$(sed -n 's/^Your code has been rated at \([-0-9.]*\)\/.*/\1/p' pylint.txt)
echo "Pylint score was $score"
anybadge --value=$score --file=assets/pylint.svg pylint
