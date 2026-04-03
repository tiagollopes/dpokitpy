from dpokitpy import Guard

guard = Guard()

texto = "CPF: 529.982.247-25 | Email: teste@gmail.com"

print(guard.is_safe(texto))
print(guard.is_safe(texto, "high"))
print(guard.is_safe(texto, "medium"))
print(guard.is_safe(texto, "low"))

print(guard.validate(texto).to_dict())
print(guard.mask(texto))
print(guard.find(texto))
for issue in guard.find(texto):
    print(issue.to_dict())
