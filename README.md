# venn-email-python

1. create new project, install mandrill and sendgrid packages
2. create mandrillService and sendgridService with send function that returns true if sent and false if error
3. create vennApiService with getKeys and getPriority functions (see https://github.com/VennHQ/venn-api)
4. create user-facing functions initalize(API_KEY) and sendEmail(from, to, subject, message)
5. for initialize(), call api.getKeys() with API_KEY passed in, and initialize services depending on what is returned
6. for sendEmail(), call api.getPriority() and redundantly send email by priority (with mandrillservice, etc. created above)
7. write documentation
8. write tests
