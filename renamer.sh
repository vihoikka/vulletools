while IFS=, read orig target; do
	mv "$orig" "$target"
done < mapping.csv

