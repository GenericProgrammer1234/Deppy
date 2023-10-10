import sys, requests, os, json

def all_files(path):
    all_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)
    return all_files

def analyze(directory):
	try:
		files = all_files(directory)
	except IndexError:
		print("Deppy: Directory does not exist")
		exit()

	imports = []

	for f in [x for x in files if x.endswith(".py")]:
		lines = open(f"{f}", "r").readlines()
		fimports = [x.split("import ")[1].split(" as")[0].strip() for x in lines if x.startswith("import ")]
		fimports.extend([x.split("from ")[1].split("import")[0].strip() for x in lines if x.startswith("from ")])
		fimports = [x for x in fimports if not "." in x]
		imports.extend(fimports)

	return sorted(set(imports))

if sys.argv[1] == "package":
	package = sys.argv[2]

	if os.path.exists(f"{os.environ['HOME']}/Library/deppy/cache/{package}.json"):
		_json = json.load(open(f"{os.environ['HOME']}/Library/deppy/cache/{package}.json", "r"))
	else:
		req = requests.get(f"https://www.pypi.org/pypi/{package}/json")

		if req.status_code == 404:
			print("Deppy: The project does not exist")
			exit()
		elif req.status_code == 500:
			print("Deppy: The PyPi API is not working, try again later")
			exit()
		else:
			_json = req.json()['info']
			json.dump(_json, open(f"{os.environ['HOME']}/Library/deppy/cache/{package}.json", "w"))

	print(f"{package} ({_json['version']})")
	print(f"Author: {_json['author']} ({_json['author_email'] or 'No email'})")
	print(f"Description: {_json['summary'] or 'No summary provided'}")
	print(f"Documentation: {_json['docs_url'] or 'No documentation link provided'}")

	requirees = _json['requires_python']

	for requires in requirees.split(","):
		if requires.startswith("=="):
			print(f"Requires Python {requires.split('==')[1]}")
		elif requires.startswith(">="):
			print(f"Requires Python {requires.split('>=')[1]} or greater")
		elif requires.startswith("<="):
			print(f"Requires Python {requires.split('<=')[1]} or lower")
		elif requires.startswith(">"):
			print(f"Requires greater then Python {requires.split('>')[1]}")
		elif requires.startswith("<"):
			print(f"Requires lower then Python {requires.split('<')[1]}")
elif sys.argv[1] == "install":
	package = sys.argv[2]

	print(f"Deppy: Starting install: {package}")
	status = os.system(f"pip install {package} > /dev/null 2>&1")
	if status != 0:
		print(f"Deppy: Installation failed: {package}")
	else:
		print(f"Deppy: Installation succeeded: {package}")
		print(f"Deppy: You can learn more by running `deppy package {package}` or `deppy analyze-package {package}`")
elif sys.argv[1] == "analyze":
	directory = sys.argv[2]

	for imp in analyze(directory):
		print(imp)
elif sys.argv[1] == "analyze-package":
	package = sys.argv[2]

	try:
		for imp in analyze(f"/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/{package}"):
			print(imp)
	except:
		print("Deppy: Package does not exist")
		exit()
