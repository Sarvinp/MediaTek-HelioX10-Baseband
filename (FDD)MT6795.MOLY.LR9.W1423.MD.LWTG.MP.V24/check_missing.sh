  while read lib
  do
    m=${lib#lib}
    m=${m%.a}
    d=$(find . -maxdepth 5 -type d -iname "$m" | head -1)
    if [ -n "$d" ]; then
      n=$(find "$d" -type f \( -name '*.c' -o -name '*.S' -o -name '*.s' \) | wc -l)
      echo "$lib $n files $d"
    fi
  done < missing_libs.txt
