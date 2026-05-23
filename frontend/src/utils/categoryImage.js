/**
 * categoryImage.js
 * Maps product name/category keywords to:
 *   - emoji (fallback)
 *   - bg (Tailwind class fallback)
 *   - unsplashQuery (for real Unsplash photo)
 */

const CATEGORY_MAP = [
  // Electronics
  { keywords: ["headphone","earphone","earbud","airpod"],      emoji:"🎧", bg:"bg-blue-50",    unsplash:"headphones music"         },
  { keywords: ["laptop","notebook","macbook","chromebook"],    emoji:"💻", bg:"bg-gray-100",   unsplash:"laptop computer"           },
  { keywords: ["phone","smartphone","iphone","android"],       emoji:"📱", bg:"bg-slate-100",  unsplash:"smartphone mobile"         },
  { keywords: ["tablet","ipad"],                               emoji:"📲", bg:"bg-indigo-50",  unsplash:"tablet device"             },
  { keywords: ["camera","dslr","mirrorless"],                  emoji:"📷", bg:"bg-zinc-100",   unsplash:"camera photography"        },
  { keywords: ["speaker","soundbar"],                          emoji:"🔊", bg:"bg-blue-100",   unsplash:"bluetooth speaker"         },
  { keywords: ["keyboard"],                                    emoji:"⌨️", bg:"bg-gray-100",   unsplash:"mechanical keyboard"       },
  { keywords: ["monitor","display","screen"],                  emoji:"🖥️", bg:"bg-gray-100",   unsplash:"computer monitor"          },
  { keywords: ["watch","smartwatch"],                          emoji:"⌚", bg:"bg-amber-50",   unsplash:"smartwatch wearable"       },
  { keywords: ["charger","cable","power bank"],                emoji:"🔌", bg:"bg-yellow-50",  unsplash:"phone charger cable"       },
  { keywords: ["tv","television"],                             emoji:"📺", bg:"bg-gray-100",   unsplash:"smart television"          },
  { keywords: ["mouse"],                                       emoji:"🖱️", bg:"bg-gray-50",    unsplash:"computer mouse"            },
  // Fashion
  { keywords: ["sneaker","shoe","boot","sandal"],              emoji:"👟", bg:"bg-orange-50",  unsplash:"sneakers shoes fashion"    },
  { keywords: ["jacket","coat","hoodie","sweater"],            emoji:"🧥", bg:"bg-red-50",     unsplash:"jacket clothing fashion"   },
  { keywords: ["shirt","t-shirt","tshirt","polo","blouse"],   emoji:"👕", bg:"bg-blue-50",    unsplash:"shirt clothing"            },
  { keywords: ["dress","skirt","gown"],                        emoji:"👗", bg:"bg-pink-50",    unsplash:"dress fashion style"       },
  { keywords: ["trouser","jean","pant","shorts"],              emoji:"👖", bg:"bg-indigo-50",  unsplash:"jeans denim fashion"       },
  { keywords: ["bag","backpack","handbag","wallet"],           emoji:"👜", bg:"bg-amber-50",   unsplash:"leather bag fashion"       },
  { keywords: ["sunglasses","glasses"],                        emoji:"🕶️", bg:"bg-yellow-50",  unsplash:"sunglasses fashion"        },
  { keywords: ["hat","cap","beanie"],                          emoji:"🧢", bg:"bg-green-50",   unsplash:"hat cap fashion"           },
  // Home & Kitchen
  { keywords: ["sofa","chair","couch"],                        emoji:"🛋️", bg:"bg-amber-50",   unsplash:"sofa couch living room"    },
  { keywords: ["desk","table","shelf"],                        emoji:"🪑", bg:"bg-yellow-50",  unsplash:"wooden desk furniture"     },
  { keywords: ["lamp","light","bulb","led"],                   emoji:"💡", bg:"bg-yellow-50",  unsplash:"lamp light interior"       },
  { keywords: ["bed","mattress","pillow","blanket"],            emoji:"🛏️", bg:"bg-blue-50",    unsplash:"bedroom bed pillow"        },
  { keywords: ["blender","mixer","juicer"],                    emoji:"🥤", bg:"bg-green-50",   unsplash:"blender kitchen appliance" },
  { keywords: ["fryer","oven","microwave"],                    emoji:"🍳", bg:"bg-orange-50",  unsplash:"oven kitchen appliance"    },
  { keywords: ["kettle","coffee","tea"],                       emoji:"☕", bg:"bg-amber-50",   unsplash:"coffee kettle kitchen"     },
  { keywords: ["pan","pot","cookware"],                        emoji:"🍳", bg:"bg-orange-50",  unsplash:"cooking pan kitchenware"   },
  { keywords: ["mug","cup","bottle"],                          emoji:"🥤", bg:"bg-cyan-50",    unsplash:"mug cup drink"             },
  { keywords: ["vacuum","cleaner"],                            emoji:"🧹", bg:"bg-purple-50",  unsplash:"vacuum cleaner home"       },
  // Sports
  { keywords: ["yoga","mat"],                                  emoji:"🧘", bg:"bg-green-50",   unsplash:"yoga mat fitness"          },
  { keywords: ["dumbbell","weight","barbell"],                 emoji:"🏋️", bg:"bg-gray-100",   unsplash:"dumbbell weights gym"      },
  { keywords: ["bicycle","bike","cycling"],                    emoji:"🚴", bg:"bg-green-50",   unsplash:"bicycle cycling sport"     },
  { keywords: ["treadmill"],                                   emoji:"🏃", bg:"bg-blue-50",    unsplash:"treadmill running gym"     },
  { keywords: ["football","soccer"],                           emoji:"⚽", bg:"bg-green-50",   unsplash:"football soccer sport"     },
  { keywords: ["basketball"],                                  emoji:"🏀", bg:"bg-orange-50",  unsplash:"basketball sport"          },
  { keywords: ["cricket"],                                     emoji:"🏏", bg:"bg-green-50",   unsplash:"cricket bat sport"         },
  { keywords: ["tennis","badminton","racket"],                 emoji:"🎾", bg:"bg-yellow-50",  unsplash:"tennis racket sport"       },
  { keywords: ["helmet"],                                      emoji:"🪖", bg:"bg-gray-100",   unsplash:"sports helmet safety"      },
  // Books
  { keywords: ["novel","fiction","book","textbook","comic"],  emoji:"📚", bg:"bg-amber-50",   unsplash:"books reading library"     },
  { keywords: ["planner","journal","diary"],                   emoji:"📓", bg:"bg-yellow-50",  unsplash:"journal notebook stationery"},
  { keywords: ["pen","pencil","marker"],                       emoji:"✏️", bg:"bg-blue-50",    unsplash:"pen pencil stationery"     },
  // Beauty
  { keywords: ["cream","moisturizer","serum","lotion"],       emoji:"🧴", bg:"bg-pink-50",    unsplash:"skincare beauty cream"     },
  { keywords: ["shampoo","conditioner","hair"],                emoji:"🧴", bg:"bg-purple-50",  unsplash:"shampoo hair care"         },
  { keywords: ["perfume","fragrance","cologne"],               emoji:"🌸", bg:"bg-rose-50",    unsplash:"perfume fragrance bottle"  },
  { keywords: ["lipstick","makeup","mascara"],                 emoji:"💄", bg:"bg-red-50",     unsplash:"makeup lipstick beauty"    },
  // Food
  { keywords: ["snack","chips","biscuit","cookie"],           emoji:"🍪", bg:"bg-yellow-50",  unsplash:"snacks cookies food"       },
  { keywords: ["chocolate","candy","sweet"],                   emoji:"🍫", bg:"bg-amber-50",   unsplash:"chocolate candy sweet"     },
  { keywords: ["beverage","juice","drink"],                    emoji:"🧃", bg:"bg-blue-50",    unsplash:"juice drink beverage"      },
  // Automotive
  { keywords: ["tyre","tire","wheel"],                         emoji:"🛞", bg:"bg-gray-100",   unsplash:"car tyre wheel"            },
  { keywords: ["car","auto","vehicle"],                        emoji:"🚗", bg:"bg-red-50",     unsplash:"car automobile"            },
  { keywords: ["tool","wrench","drill"],                       emoji:"🔧", bg:"bg-gray-100",   unsplash:"tools wrench hardware"     },
  // Pets
  { keywords: ["dog","puppy"],                                 emoji:"🐶", bg:"bg-amber-50",   unsplash:"dog puppy pet"             },
  { keywords: ["cat","kitten"],                                emoji:"🐱", bg:"bg-orange-50",  unsplash:"cat kitten pet"            },
  { keywords: ["fish","aquarium"],                             emoji:"🐠", bg:"bg-blue-50",    unsplash:"fish aquarium"             },
  { keywords: ["pet"],                                         emoji:"🐾", bg:"bg-amber-50",   unsplash:"pet animal"                },
  // Toys
  { keywords: ["lego","block"],                                emoji:"🧱", bg:"bg-red-50",     unsplash:"lego blocks toys"          },
  { keywords: ["puzzle"],                                      emoji:"🧩", bg:"bg-purple-50",  unsplash:"puzzle game toy"           },
  { keywords: ["toy","doll","figure"],                         emoji:"🪆", bg:"bg-pink-50",    unsplash:"toys children play"        },
]

const DEFAULT = { emoji:"🛍️", bg:"bg-gray-100", unsplash:"shopping product" }

// Unsplash Source — completely free, no API key needed
// Returns a deterministic image based on the query + product id seed
export function getUnsplashUrl(name = "", category = "", id = "", size = 400) {
  const text = `${name} ${category}`.toLowerCase()
  let entry = DEFAULT
  for (const e of CATEGORY_MAP) {
    if (e.keywords.some(kw => text.includes(kw))) { entry = e; break }
  }
  // Use a numeric seed from the product id for variety within a category
  const seed = id ? parseInt(id.replace(/\D/g, "").slice(0, 6) || "1") : 1
  return `https://source.unsplash.com/${size}x${size}/?${encodeURIComponent(entry.unsplash)}&sig=${seed}`
}

export function getProductVisual(name = "", category = "") {
  const text = `${name} ${category}`.toLowerCase()
  for (const entry of CATEGORY_MAP) {
    if (entry.keywords.some(kw => text.includes(kw))) {
      return { emoji: entry.emoji, bg: entry.bg }
    }
  }
  return DEFAULT
}
