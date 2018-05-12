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

  async componentDidLoad() {
    console.log('ej-conversation componentDidLoad antes')
    this.setUpConversation();
    console.log('ej-conversation componentDidLoad depois')
  }

  async setUpConversation() {
    try {
      this.conversation = await fetchConversation();
    }
    catch (err) {
      console.log(err);
    }
  }

  render() {
    if (this.conversation) {
      return (
        <div class='ej-conversation'>
          <div class="ConversationDetail">
            <div class="ConversationDetail-banner">
              <h1>{ this.conversation.title }</h1>
              <ul class="ConversationDetail-statistics">
                <li>1</li>
                <li>3</li>
              </ul>
            </div>
            <div class="ConversationDetail-arrow"></div>

            <ul class="ConversationDetail-statisticsBottom">
              <li>
                <div>Categoria</div>
                <div>Tecnica</div>
              </li>
              <li>veja mais categorias</li>
            </ul>
            <div class="ConversationDetail-header">
              <h1>Opiniões da comunidade</h1>
              <p>Interaja com as opiniões da comunidade selecionando um dos botões
                de opção.</p>
            </div>
          </div>
        </div>
        );
    }
  }
}
