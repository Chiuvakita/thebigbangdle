import random
from django.shortcuts import render, redirect
from django.http import JsonResponse

# ==========================
# AUTOCOMPLETE
# ==========================
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
        "pista": "Bazinga! Físico teórico; compañero de Leonard.",
        "genero": "Hombre",
        "ocupacion": "Físico teórico",
        "nacionalidad": "Estadounidense",
        "pelo": "Castaño",
        "relacion": "Amy",
    },
    "leonard": {
        "pista": "Físico experimental; usa gafas y vive con Sheldon.",
        "genero": "Hombre",
        "ocupacion": "Físico experimental",
        "nacionalidad": "Estadounidense",
        "pelo": "Castaño",
        "relacion": "Penny",
    },
    "penny": {
        "pista": "Vecina de enfrente, actriz/mesera; luego vendedora.",
        "genero": "Mujer",
        "ocupacion": "Actriz / Mesera",
        "nacionalidad": "Estadounidense",
        "pelo": "Rubio",
        "relacion": "Leonard",
    },
    "howard": {
        "pista": "Ingeniero aeroespacial con madre muy presente.",
        "genero": "Hombre",
        "ocupacion": "Ingeniero aeroespacial",
        "nacionalidad": "Estadounidense",
        "pelo": "Castaño",
        "relacion": "Bernadette",
    },
    "raj": {
        "pista": "Astrofísico que al inicio no podía hablar con mujeres.",
        "genero": "Hombre",
        "ocupacion": "Astrofísico",
        "nacionalidad": "Indio",
        "pelo": "Negro",
        "relacion": "Soltero",
    },
    "amy": {
        "pista": "Neurocientífica, pareja de Sheldon.",
        "genero": "Mujer",
        "ocupacion": "Neurocientífica",
        "nacionalidad": "Estadounidense",
        "pelo": "Castaño",
        "relacion": "Sheldon",
    },
    "bernadette": {
        "pista": "Microbióloga con voz dulce y carácter fuerte.",
        "genero": "Mujer",
        "ocupacion": "Microbióloga",
        "nacionalidad": "Estadounidense",
        "pelo": "Rubio",
        "relacion": "Howard",
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
    }

    if request.method == "POST":
        # Botón "Reiniciar juego"
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

        # guardar resultado en sesión
        is_ok = guess in VARIANTS.get(secret, set())
        request.session["last_result"] = (
            f"¡Correcto! Era {secret.title()} 🎉" if is_ok else "Ups, intenta de nuevo."
        )
        request.session["is_correct"] = is_ok

        if is_ok:
            _reset_secret(request)

        return redirect("home")

    # en GET recuperamos el último resultado
    ctx["result"] = request.session.pop("last_result", None)
    ctx["is_correct"] = request.session.pop("is_correct", False)

    return render(request, "templatesApp/index.html", ctx)
