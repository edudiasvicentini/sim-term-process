exe:
	pyinstaller main.py

test:
	python3 -m unittest

clean:
	-rm -r dist build main.spec

fresh:
	-rm -r dist build main.spec
	pyinstaller main.py
