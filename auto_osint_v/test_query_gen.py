from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained('BeIR/query-gen-msmarco-t5-large-v1')
model = T5ForConditionalGeneration.from_pretrained('BeIR/query-gen-msmarco-t5-large-v1')

para = """
Since the start of March 2023, Russia has likely launched at least 71 Iranian-designed Shahed series one-way attack uncrewed aerial vehicle (OWA-UAVS) against targets across Ukraine.
These attacks followed a two-week pause in OWA-UAV attacks in late February 2023. Russia has likely started receiving regular resupplies of small numbers of Shahed OWA-UAVs.
Russia is likely launching Shaheds from two axes: from Russia’s Krasnodar Krai in the east and from Bryansk Oblast in the north-east.
This allows Russia flexibility to target a broad sector of Ukraine and decreases flying time to targets in the north of Ukraine. It is also likely to be a further attempt to stretch Ukrainian air defences.
       """

input_ids = tokenizer.encode(para, return_tensors='pt')
outputs = model.generate(
    input_ids=input_ids,
    max_length=240,
    do_sample=True,
    top_p=0.95,
    num_return_sequences=10)    # Returns 10 queries

print("Paragraph:")
print(para)

print("\nGenerated Queries:")
for i in range(len(outputs)):
    query = tokenizer.decode(outputs[i], skip_special_tokens=True)
    print(f'{i + 1}: {query}')
