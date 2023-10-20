# discord-bot-eth-gas

Ce script Python est conçu pour surveiller les prix du gas Ethereum (Gwei) et du gas Bitcoin (sats/vB) sur les réseaux respectifs. Il permet également de définir des seuils d'alerte pour les prix du gas Ethereum et de recevoir des notifications Discord lorsque les seuils sont atteints.

## Installation

Assurez-vous d'installer les dépendances requises en utilisant `pip`. Vous pouvez le faire en exécutant la commande suivante :

   ```bash
   pip install -r requirements.txt
   ```
Créez un fichier .env à la racine de votre projet et ajoutez les variables d'environnement suivantes :
   HTTP_PROVIDER: Le fournisseur HTTP pour votre nœud Ethereum.
   DISCORD_BOT_TOKEN: Le token de votre bot Discord.

Exemple de fichier .env :  
    ```
    HTTP_PROVIDER=https://your-ethereum-node-url  
    DISCORD_BOT_TOKEN=your-discord-bot-token
    ```
## Utilisation

Exécutez le script Python en utilisant la commande suivante :

   ```bash
python votre_script.py
   ```

Le bot Discord utilise le préfixe ! pour exécuter des commandes. Voici quelques commandes disponibles :

    !get_sat: Affiche le prix du gas sur Bitcoin.
    !get_gwei: Affiche le prix actuel du gas sur Ethereum.
    !set_alert [threshold]: Définit un seuil d'alerte pour le prix du gas en Gwei.
    !get_alert: Affiche le seuil d'alerte actuellement défini.
    !del_alert: Supprime le seuil d'alerte actuellement défini.
    !help_gas: Affiche la liste des commandes disponibles.
