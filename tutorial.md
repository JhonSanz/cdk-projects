### How to start

1. Install aws cdk with `npm install -g aws-cdk`
2. Init a sample app with `cdk init sample-app --language python`
3. code your infrastructure
4. run `cdk bootstrap` initialice aws resources we need as part of this project.
5. run `cdk synth` to generate the real .yaml which shows you all the details and settings behind the sceens that are going to be created. It is perfect for testing, because tests look for this yaml file, and extract all the needed data from it
6. run `cdk diff` to verify against Cloud Formation what you have and it shows what is going to change. If you want to keep this file in your SO you can run `cdk diff --no-color &> diff.txt`
7. run `cdk deploy`. It is going to show all details about what is going to be created
8. Enjoy

# Bonus **MUY IMPORTANTE**

- run `ckd destroy` to delete all we created 🎉
