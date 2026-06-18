---
title: "Why Typedef Is Used For Structs In C"
date: 2016-10-18
categories: ["embedded systems"]
---
At first glance, adding a typedef to a struct in C seems to complicate the definition. However, it simplifies the declaration of the structure. This is not always recommend, as it can add a layer of obfuscation.

### Structures

Here is how a normal structure is defined in C.
    
    
    #include <stdio.h>
    #include <string.h>
    
    struct Cat {      // defining Cat structure
      char name[20];  // members of Cat structure
      int age;
      int weight;
    };
    
    int main() {
      struct Cat myCat;  // declaring Cat structure, myCat
      
      strcpy( myCat.name, "Cleopatra");  // setting member values
      myCat.age = 4;
      myCat.weight = 10;
    
      return 0;
    
    }
    
    

In the example above, notice declaring myCat on Line 11 is "struct Cats myCat". We are about to see how typedef will shorten this.

### Typedef
    
    
    #include <stdio.h>
    #include <string.h>
    
    typedef struct {  // defining Cat structure
      char name[20];  // members of Cat structure
      int age;
      int weight;
    } Cat;
    
    int main() {
      Cat myCat; // declaring Cat structure, myCat
    
      strcpy( myCat.name, "Cleopatra"); // setting member values
      myCat.age = 4;
      myCat.weight = 10;
    
    return 0;
    }
    

Notice how Line 11 has shortened to "Cat myCat".

When declaring many structs throughout a large project, this can save some typing and sometimes increase readability.

### Criticism

Typedefs on structure isn't popular with everyone. Most prominently, the Linux kernel does not use typedefs for structures. A quote from the [Linux Kernel Coding Style](<https://www.kernel.org/doc/Documentation/CodingStyle>):

_" It's a **mistake** to use typedef for structures and pointers. When you see a

.. code-block:: c

vps_t a;

in the source, what does it mean?  
In contrast, if it says

.. code-block:: c

struct virtual_container *a;

you can actually tell what "a" is."_

Nonetheless, you are sure to encounter typedef structures. Try not to add any more to the world.
