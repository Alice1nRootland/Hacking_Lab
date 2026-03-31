<img width="496" height="496" alt="image" src="https://github.com/user-attachments/assets/46e96d00-2bc2-48ee-82f9-fc8979b50dd4" />

the given file 

<img width="1597" height="285" alt="image" src="https://github.com/user-attachments/assets/f31bc3ee-6632-4a82-9315-c0e340a3edbb" />

i use this script on sage cell server [Sage Cell Server](https://sagecell.sagemath.org/)

```php
# 1. The Data
C = [261015377840097129644656095565685376500800808766108344312889890941881310406271029674014793397545165103395343855878275207466640295235630881234460087301347548215563188593349651827640750082989109168948218090823688728120191946368830079650038127582609716950748457986306745462478700140482424602747673350135482784842046711853935789064304208838611776643995224028688332945173847204751554918821126287440606598775126110616095112715429594654136273602201811725670850771582717890050469270, 765414195187859052619533244516588678060823972807551164301189387961500669966532884232388416796722451978051904514262487164294349143001757689551444872882259138199099972792035090674549898567043079460244470017687664485244329840687870776933939805259347130127175804394955357253682057083493183324893129082911966172786903953739660045488379397629550253845249651036049776596843191185343404052537674328814034153042063558369229044261101250385331413638318501488056913514137437495172681456, 210048875537164620748767169827273158934838917533187807007677485753382330073843878232475339716761320572785480054088254601030283221339573845220426671074628037510203160112233730823176626312540707759454201584404136437591279142829041289844172542532372477473893208931428384640236718980995638257615019157682188371726862076665874249277888833635635282578754367326314629690797366547945435130436363963925485304566764113495928731220535645614970688240672848759549573126819671090844315965, 738270505985269085166962351671278779087272452784304213909215178082858583440646894395998303617915677978863975684565271892915195279775135582241368066550913913438696958954002638381237163934616874044683342940605394641866861352737056857398657432183532186630544806981689403503353445187996801403260445967408804300839623373071605062790915495993502363712283851708857156274182049366636407437242329264619213719096869156224651240104685529069513873263720720072012001388136668338541805338, 9585332443594819517663976420342469583738673558473574728070642143862960993198089742890896991220826299790452545757892998231197572680708844096419875621625011670061443217260848535942570822836031081309415113710776413535025832642133692575065045601281722556803379766962186736693424018047379452130587877860632867286419577116562191878783299356990125584593341872592608699683752571156749941467232908224109559932502888433782272943996206542463856677689351734745874447442230346003476717]

# 2. Conversion Helper
def to_bytes(n):
    n = int(abs(n))
    return n.to_bytes((n.bit_length() + 7) // 8, 'big')

# 3. Lattice Setup
# We use K=2^256 to balance the first column with the noise terms
K = 2**256
n = len(C)
L = Matrix(ZZ, n, n)
L[0, 0] = K
for i in range(1, n):
    L[0, i] = C[i]
    L[i, i] = -C[0]

print("[*] Reducing lattice (Balanced Weights)...")
L_red = L.LLL()

# 4. Intelligent Search
print("[*] Filtering results for actual flag...")
for row in L_red:
    a0 = abs(row[0]) // K
    # If a0 is 1 or 0, it's a trivial basis vector, not the secret multiplier
    if a0 <= 1: 
        continue
    
    # Recover M
    m = C[0] // a0
    
    # Check a few offsets around m
    for offset in range(-2, 3):
        res = to_bytes(m + offset)
        # Stricter verification: flag must contain 'flag{' or similar common ASCII
        if b"flag{" in res or b"CTF{" in res or (b"{" in res and b"}" in res):
            print("\n" + "#"*40)
            print(f"[!] SUCCESS! Found at offset {offset}")
            print(f"Multiplier A0: {a0}")
            print(f"Flag: {res.decode('utf-8', errors='ignore')}")
            print("#"*40)
            break

print("[*] Search complete.")
```

# What the original challenge does

The challenge code:

```
print([ int(flag) *randbits(1024) +randbits(256) ... ])
```

Mathematically each output is:

```
Ci = m * ki + ri

```

where

- `m` = flag interpreted as a big integer
- `ki` = 1024‑bit random multiplier (large)
- `ri` = 256‑bit random noise (small)
- 5 samples are given

This is **hidden number problem (HNP)** / **approximate common divisor problem**:

> We see only noisy multiples of the same hidden number m
> 
> 
> Recover m knowing noise is small.
> 

---

# What your script is trying to do

It performs **balanced-lattice approximate GCD attack**:

- construct lattice expressing relationships between samples
- use LLL to find a short vector that encodes `ki`
- divide to solve for m
- check for flag‑like bytes

This is the same math idea as Howgrave‑Graham AGCD.

---

# Script explanation section‑by‑section

---

## 1. Load ciphertext values (the Ci’s)

```
C = [...]
```

These are exactly your 5 outputs from the chal script.

---

## 2. Helper to convert big int → bytes

```
defto_bytes(n):
    n =int(abs(n))
    return n.to_bytes((n.bit_length() +7) //8,'big')
```

Purpose:

- flags live as bytes
- LLL gives integers
- need to convert to printable form

---

## 3. Build lattice for approximate common divisor

```
K=2**256
n=len(C)
L=Matrix(ZZ,n,n)
L[0,0]=K
foriinrange(1,n):
L[0,i]=C[i]
L[i,i]=-C[0]
```

### Why 2²⁵⁶?

Noise `ri` is 256‑bit:

```
ri <2^256
```

So multiplying first basis vector by `2^256`:

- balances matrix norm
- prevents flag from vanishing under reduction
- standard lattice balancing trick

### Matrix conceptually

The lattice expresses equations like:

```
C0 * k − Ci * k' ≈ small noise
```

LLL will find **small relations**, which hint the hidden divisor.

This turns AGCD → lattice small‑vector search.

---

## 4. Run LLL

```
print("[*] Reducing lattice (Balanced Weights)...")
L_red = L.LLL()
```

LLL finds **short vectors** in lattice basis.

Short vectors correspond to:

```
k0*C0 − k1*C1 ≈ small noise
```

Since:

```
Ci = ki*m + r

```

we get:

```
k0*(k0*m + r0) − k1*(k1*m + r1)
= (k0*k0 − k1*k1)*m + (k0*r0 − k1*r1)
≈ multiple of m + small thing
```

So…

short vector ≈ multiple of m

---

## 5. Extract candidate multiplier `a0`

```
for row in L_red:
    a0 =abs(row[0])// K
if a0 <=1:
continue
```

Explanation:

- first column holds scaled multiple hypothesis
- divide by `K` to rescale
- skip trivial vectors (0 or 1)

This `a0` should be approximately the random 1024‑bit multiplier.

---

## 6. Recover `m`

```
m = C[0] // a0
```

Because:

```
C0 = m*k0 + noise
≈ m*k0
```

So:

```
m ≈ C0 / k0
```

Integer division corrects noise if lattice recovered good k0.

---

## 7. Local search (correct off-by-one errors)

```
foroffset inrange(-2,3):
    res =to_bytes(m + offset)
```

Noise can shift m slightly — this tight search fixes rounding errors.

---

## 8. Recognize flag automatically

```
ifb"flag{"in resorb"CTF{"in resor (b"{"in resandb"}"in res):
```

This checks:

- standard `flag{`
- or any `{...}` token
- or CTF alphabet

Then prints win condition.

<img width="1892" height="608" alt="image" src="https://github.com/user-attachments/assets/146ef8fc-7600-4052-9501-b8b0b9cb19e4" />

• **Flag:** `RE:CTF{ApprOx1m@t3_C0mm0n_D1v1s0r_1n5t34d_0F_Gr3at3s7_COmm0N_Div1s0R}`
