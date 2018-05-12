const fetchConversation = () => {
  const url = `http://localhost:3000/conversations/random`;

  return fetch(url).then((res) => {
    console.log('fetchConversation 1: ', res)
    return res.json()
  })
}

export { fetchConversation };