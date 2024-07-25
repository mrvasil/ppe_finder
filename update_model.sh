read -p "REMOVE? OLD MODEL AND DOWNLOAD THE NEWEST ONE FROM HUGGINGFACE? (Y/N): " confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
rm base.pt extra.pt train_dataset.csv train_dataset_extra.csv
clear
wget https://huggingface.co/tmasikt/ppe-classificator/resolve/main/base.pt
wget https://huggingface.co/tmasikt/ppe-classificator/resolve/main/extra.pt
wget https://huggingface.co/tmasikt/ppe-classificator/resolve/main/train_dataset_extra.csv
wget https://huggingface.co/tmasikt/ppe-classificator/resolve/main/train_dataset.csv
clear
echo "DONE. #"