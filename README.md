# Code converter
This advanced code converter 
translates Python to Shell.
It is capable of handling most translations.

### Example input (in Python)

```python
# Greet a user multiple times
name = input("Enter your name: ")
count = 3

for i in range(count):
    print("Hello", name, i)

if name == "Alice":
    print("Welcome back!")
elif name == "Bob":
    print("Hey Bob!")
else:
    print("Who are you?")
```

### Example output (in Shell)

```bash
# Greet a user multiple times
read -p "Enter your name: " name
count=3

for i in $(seq 0 $((count - 1))); do
  echo "Hello $name $i"
done

if [ "$name" = "Alice" ]; then
  echo "Welcome back!"
elif [ "$name" = "Bob" ]; then
  echo "Hey Bob!"
else
  echo "Who are you?"
fi
```
#### Using the translator is easy and fun. Simply copy and paste Translator.py into a Python module.
#### This repo was made with partial assistance from ChatGPT.
