import { Component, State } from '@stencil/core';
import { fetchConversation } from '../../global/http-service';
import { ConversationModel } from '../../global/interfaces';


@Component({
  tag: 'ej-conversation',
  styleUrl: 'ej-conversation.scss',
  shadow: true
})
export class Conversation {
  
  @State() conversation: ConversationModel;

  // @Prop({ connect: 'ion-toast-controller' }) toastCtrl: ToastController;
  // @Element() el: Element;

  async componentDidLoad() {
    console.log('ej-conversation componentDidLoad antes')
    this.setUpConversation();
    console.log('ej-conversation componentDidLoad depois')
  }

  async setUpConversation() {
    // set up with first bit of content
    try {
      this.conversation = await fetchConversation();
      console.log('wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')
      console.log(this.conversation);
    }
    catch (err) {
      console.log(err);
      // this.showErrorToast();
    }
  }

  render() {
    if (this.conversation) {
      return (
        <div class='ej-conversation'>
          <p>
            Minha conversa é {this.conversation.title}
          </p>
          <div class='bli'>
            <h1>Titulo Grande</h1>
            testando conteudo com variavel global
          </div>
        </div>
        );
    }
  }
}
