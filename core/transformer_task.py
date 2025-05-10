from task import RequestedWorkTask
from constants import *
from os.path import join
from pathlib import Path
from os import getcwd
from datasets import Dataset
from scipy.special import softmax
import evaluate

import torch
import numpy as np

from transformers import AutoTokenizer, AutoModelForSequenceClassification, \
    TrainingArguments, Trainer, DataCollatorWithPadding, \
    EarlyStoppingCallback, pipeline

f1 = evaluate.load("f1")

class TransformerTask(RequestedWorkTask):
    pipeline = None
    task_type = None
    model_name = None
    dataset_url = None
    id_dict = None
    label_dict = None
    model_path = None
    output_dir = None
    batch_size = None

    def set_params(self, configuration_json:str):
        super().set_params(configuration_json)

        self.task_type = self.params[task_type_key]
        self.model_name = self.params[model_name_key]
        self.dataset_url = self.params[dataset_url_key]
        self.id_dict = self.params[id_dict_key]
        self.label_dict = self.params[label_dict_key]
        self.batch_size = self.params[batch_size_key]

        if len(self.model_name) == 0:
            self.model_name = None
        else:        
            self.model_path = join(getcwd(), "models", self.task_type, self.model_name)
            self.output_dir = join(getcwd(), "output", self.task_type, self.model_name)  

            for path_to_check in [self.model_path, self.output_dir]:
                path = Path(path_to_check)     
                path.mkdir(parents=True, exist_ok=True)


    def get_model_and_data_task(self, train, test):        
        id2label = self.id_dict
        label2id = self.label_dict
        model_type = self.task_type

        model = AutoModelForSequenceClassification.from_pretrained(
            self.model_path,
            num_labels=len(id2label), id2label=id2label, label2id=label2id,
            ignore_mismatched_sizes=True,
            problem_type=model_type)
        tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

        def tokenize_function(examples):
            return tokenizer(examples["text"], 
                             padding=True, 
                             truncation=True, 
                             max_length=MAX_SEQUENCE_LEN)

        for_train = Dataset.from_pandas(train).map(
            tokenize_function, batched=True)
        for_test = Dataset.from_pandas(test).map(
            tokenize_function, batched=True)

        return (model, tokenizer, data_collator, for_train, for_test)


    def get_training_setup(self, model, 
                           for_train, for_test, 
                           tokenizer, data_collator, 
                           compute_metrics):
        
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            learning_rate=2e-5,
            per_device_train_batch_size=self.batch_size,
            per_device_eval_batch_size=self.batch_size,
            num_train_epochs=50,
            weight_decay=0.01,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            save_total_limit=1,
            load_best_model_at_end=True,
            push_to_hub=False,
            resume_from_checkpoint=True
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=for_train,
            eval_dataset=for_test,
            tokenizer=tokenizer,
            data_collator=data_collator,
            compute_metrics=compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
        )

        return trainer

    def start_working(self):
        train = None
        test = None
        to_predict = None

        if self.model_name == None:
            pipeline(self.task_type, model=None)('hugging face is the best')
            return
        else:
            torch.cuda.empty_cache()
            (model, tokenizer, data_collator, for_train,for_test) = self.get_model_and_data_task(train, test)
            
            def compute_metrics(eval_pred):
                predictions, labels = eval_pred
                predictions = np.argmax(predictions, axis=1)
                
                return f1.compute(predictions=predictions, references=labels)

            trainer = self.get_training_setup(
                model, for_train, for_test, 
                tokenizer, data_collator,
                compute_metrics)
            _ = trainer.train()

            torch.cuda.empty_cache()

            self.result_values = {}
            for _, row in to_predict.iterrows():
                text = row[text_key]
                text_id = row[text_id_key]
                inputs = tokenizer(text, return_tensors="pt")
                outputs = model(**inputs)

                probabilities = softmax(
                        outputs[0].cpu().detach().numpy(), axis=1)[0]
                
                predicted_label = int(probabilities.argmax())

                self.result_values[text_id] = predicted_label

