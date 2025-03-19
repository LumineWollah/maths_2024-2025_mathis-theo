from quaternion import Quaternion

def main():
    print("=== Démonstration des Quaternions ===")
    
    q1 = Quaternion(1, 2, 3, 4)
    q2 = Quaternion(5, 6, 7, 8)
    print(f"q1: {q1}")
    print(f"q2: {q2}")
    
    print("\nAddition:")
    print(q1 + q2)
    
    print("\nSoustraction:")
    print(q1 - q2)
    
    print("\nMultiplication de quaternions:")
    print(q1 * q2)
    
    print("\nMultiplication par un scalaire (2):")
    print(q1 * 2)
    
    print("\nConjugué de q1:")
    print(q1.conjugate())
    
    print("\nNorme de q1:")
    print(q1.norm())
    
    print("\nNormalisation de q1:")
    print(q1.normalize())
    
    print("\nRotation du vecteur (1, 0, 0) avec q1:")
    print(q1.rotate_vector((1, 0, 0)))
    
    print("\nMatrice de rotation de q1:")
    for row in q1.to_rotation_matrix():
        print(row)
    
    print("\nGénération d'un quaternion aléatoire:")
    print(Quaternion.random())
    
if __name__ == "__main__":
    main()
