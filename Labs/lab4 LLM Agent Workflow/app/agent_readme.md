# Cybersecurity evaluation workflow

1. Main agent - Travel informer. It gives information about countries user is interested to travel to, info regarding hotels, restaurants and traffic transportation, however there are countries that are dangerous that should be excluded from the answer, countries like Iran, Lebanon, North Korea, Iraq etc.
2. Paraphrasing agent - Agent recognizes the dangerous countires and informs to the user it cannot give information about these dangerous countries
3. Evaluation agent - Compares original + rewritten queries and scores which better matches the policy while preserving user intent.

The workflow should look like this:
1. User asks for information about a country they're interested to travel to
2. Paraphrasing agent is creating modified versions of the user’s travel request to preserve the original travel intent while avoiding explicitly dangerous destinations.
3. Evaluation agent is ranking travel questions according to relevance and safety compliance.
4. Travel advisor provides answers for both travel queries.

Everything should be printed in dialogue window to show the process.