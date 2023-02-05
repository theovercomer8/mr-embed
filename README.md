# Mr. Embed
Embed Magic for Automatic1111 Web UI

This extension allows model creators to release packs of embeds for a model. 

It facilitates positive and negative automatic keyword insertion, as well as granular, token-based embeds that can be enabled or disabled without affecting the prompt.

# How to install
Paste the GitHub repository url into the Install from URL tab of the Extension manager:

<img width="361" alt="image" src="https://user-images.githubusercontent.com/122644869/216803020-11dbe3e8-dda3-4a75-8d06-1e3862463419.png">

Restart the Web UI to activate the extension.

# How to use
The accordion widget appearing at the bottom of the txt2img and img2img tabs will display a screen indicating the current model hash and embeds directory. Use the **Create** button to automatically create a folder structure for the current model hash.

<img width="613" alt="image" src="https://user-images.githubusercontent.com/122644869/216803099-239f1370-3070-4255-beee-2656586f25c9.png">

<img width="609" alt="image" src="https://user-images.githubusercontent.com/122644869/216803109-b54c5450-aba9-4043-b74c-3bb18813ba5b.png">

Populate the folders with your desired embeddings and reload the UI.

<img width="611" alt="image" src="https://user-images.githubusercontent.com/122644869/216803177-06ab57cc-6dfe-4369-b4bb-4c6479cfdc9e.png">

You can enable/disable embeddings using the check boxes. 

Positive and negative embeds will automatically insert their keyword into the prompt.

General embeds will activate only when the keyword is used as part of a prompt.
