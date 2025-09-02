import random
from django.shortcuts import render, redirect
from django.http import JsonResponse

def autocomplete(request):
    q = request.GET.get("q", "").lower()
    if not q:
        return JsonResponse([], safe=False)

    results = [n for n in ALL_NAMES if q in n.lower()]
    return JsonResponse(results, safe=False)

# ==========================
# DATA
# ==========================
CHARACTERS = {
    "sheldon": {
        "pista": "No es el mayor del grupo, pero su edad mental parece diferente.",
        "genero": "Hombre",
        "ocupacion": "Físico teórico",
        "nacionalidad": "Estadounidense",
        "pelo": "Castaño",
        "relacion": "Amy",
        "imagen": "imagenes/sheldon.jpg",
    },
    "leonard": {
        "pista": "No suele liderar, pero siempre termina en el centro de las discusiones.",
        "genero": "Hombre",
        "ocupacion": "Físico experimental",
        "nacionalidad": "Estadounidense",
        "pelo": "Castaño",
        "relacion": "Penny",
        "imagen": "imagenes/leonard.jpg",
    },
    "penny": {
        "pista": "Nunca fue reconocida por sus estudios académicos, pero aun así influye en todos.",
        "genero": "Mujer",
        "ocupacion": "Actriz / Vendedora",
        "nacionalidad": "Estadounidense",
        "pelo": "Rubio",
        "relacion": "Leonard",
        "imagen": "imagenes/penny.jpg",
    },
    "howard": {
        "pista": "Comparte más cosas con su madre de las que le gustaría admitir.",
        "genero": "Hombre",
        "ocupacion": "Ingeniero aeroespacial",
        "nacionalidad": "Estadounidense",
        "pelo": "Castaño",
        "relacion": "Bernadette",
        "imagen": "imagenes/howard.jpg",
    },
    "raj": {
        "pista": "Habla de sentimientos más que de ciencia, pero sigue siendo científico.",
        "genero": "Hombre",
        "ocupacion": "Astrofísico",
        "nacionalidad": "Indio",
        "pelo": "Negro",
        "relacion": "Soltero",
        "imagen": "imagenes/raj.jpg",
    },
    "amy": {
        "pista": "No siempre fue parte del grupo, pero acabó siendo indispensable.",
        "genero": "Mujer",
        "ocupacion": "Neurocientífica",
        "nacionalidad": "Estadounidense",
        "pelo": "Castaño",
        "relacion": "Sheldon",
        "imagen": "imagenes/amy.jpg",
    },
    "bernadette": {
        "pista": "Pequeña en tamaño, pero no en personalidad.",
        "genero": "Mujer",
        "ocupacion": "Microbióloga",
        "nacionalidad": "Estadounidense",
        "pelo": "Rubio",
        "relacion": "Howard",
        "imagen": "imagenes/bernadette.jpg",
    },
    "stuart": {
        "pista": "Siempre está cerca de los cómics, pero no siempre del éxito.",
        "genero": "Hombre",
        "ocupacion": "Dueño de tienda de cómics",
        "nacionalidad": "Estadounidense",
        "pelo": "Castaño",
        "relacion": "Soltero",
        "imagen": "imagenes/stuart.jpg",
    },
    "beverly": {
        "pista": "Su forma de criar es tan científica como fría.",
        "genero": "Mujer",
        "ocupacion": "Psiquiatra / Autora",
        "nacionalidad": "Estadounidense",
        "pelo": "Rubio",
        "relacion": "Madre de Leonard",
        "imagen": "imagenes/beverly.jpg",
    },
    "emily": {
        "pista": "Interesada en lo macabro, pero aún así formó pareja dentro del grupo.",
        "genero": "Mujer",
        "ocupacion": "Dermatóloga",
        "nacionalidad": "Estadounidense",
        "pelo": "Pelirrojo",
        "relacion": "Raj",
        "imagen": "imagenes/emily.jpg",  
    },
    "leslie": {
        "pista": "Científica con opiniones fuertes, suele discutir con Sheldon.",
        "genero": "Mujer",
        "ocupacion": "Física experimental",
        "nacionalidad": "Estadounidense",
        "pelo": "Castaño",
        "relacion": "Leonard (ocasional)",
        "imagen": "imagenes/leslie.jpg",
    },
    "wil_wheaton": {
        "pista": "No es científico, pero es recordado por su papel en otra galaxia.",
        "genero": "Hombre",
        "ocupacion": "Actor / Él mismo",
        "nacionalidad": "Estadounidense",
        "pelo": "Castaño",
        "relacion": "Enemigo-amigo de Sheldon",
        "imagen": "imagenes/wil.jpg",
    },
}

VARIANTS = {
    "sheldon": {"sheldon", "sheldon cooper"},
    "leonard": {"leonard", "leonard hofstadter"},
    "penny": {"penny"},
    "howard": {"howard", "howard wolowitz"},
    "raj": {"raj", "rajesh", "raj koothrappali"},
    "amy": {"amy", "amy farrah fowler"},
    "bernadette": {"bernadette", "bernadette rostenkowski"},
    "stuart": {"stuart", "stuart bloom"},
    "beverly": {"beverly", "beverly hofstadter"},
    "emily": {"emily", "emily sweeney"},
    "leslie": {"leslie", "leslie winkle"},
    "wil_wheaton": {"wil wheaton", "wheaton"},
}

ALL_NAMES = sorted({v for vs in VARIANTS.values() for v in vs})

# ==========================
# HELPERS
# ==========================
def _pick_secret(request):
    if "secret_char" not in request.session:
        request.session["secret_char"] = random.choice(list(CHARACTERS.keys()))
        request.session["attempts"] = []
    return request.session["secret_char"]

def _reset_secret(request):
    request.session["secret_char"] = random.choice(list(CHARACTERS.keys()))
    request.session["attempts"] = []

# ==========================
# VIEW INDEX
# ==========================
def index(request):
    secret = _pick_secret(request)
    secret_data = CHARACTERS[secret]

    ctx = {
        "hint": secret_data["pista"],
        "result": None,
        "is_correct": False,
        "last_guess": "",
        "all_names": ALL_NAMES,
        "suggestions": [],
        "attempts": request.session.get("attempts", []),
        "imagen": None,
    }

    if request.method == "POST":
        if "reset" in request.POST:
            _reset_secret(request)
            return redirect("home")

        guess = (request.POST.get("guess") or "").strip().lower()
        ctx["last_guess"] = guess

        # detectar personaje
        guess_key = None
        for k, vs in VARIANTS.items():
            if guess in vs:
                guess_key = k
                break

        if guess_key:
            guess_data = CHARACTERS[guess_key]
            comparisons = {
                field: guess_data[field] == secret_data[field]
                for field in ["genero", "ocupacion", "nacionalidad", "pelo", "relacion"]
            }
            comparisons["nombre"] = guess_key == secret

            attempt = {
                "nombre": guess_key.title(),
                "data": guess_data,
                "comparisons": comparisons,
            }
            attempts = request.session.get("attempts", [])
            attempts.insert(0, attempt)
            request.session["attempts"] = attempts

        # Verificar acierto
        is_ok = guess in VARIANTS.get(secret, set())
        ctx["is_correct"] = is_ok
        ctx["result"] = f"¡Correcto! Era {secret.title()} 🎉" if is_ok else "Ups, intenta de nuevo."

        if is_ok:
            ctx["imagen"] = CHARACTERS[secret]["imagen"]

    return render(request, "templatesApp/index.html", ctx)
