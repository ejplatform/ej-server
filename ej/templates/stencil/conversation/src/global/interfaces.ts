export interface ConversationModel {
  title: string,
  slug: string,
  body: string,
  statistics: any,
  category_name: string
}

export interface CommentModel {
  id: number,
  author_name: string,
  content: string,
  // category_name: string
}

export class VoteModel {

  static AGREE = 1;
  static PASS = 0;
  static DISAGREE = -1;

  id: number;
  comment: number|string;
  value: number|string;
  created_at: string;

}