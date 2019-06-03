import React from "react";
import styles from "./chatStyles.css";

const MessageBubble = props => {
  let image;
  if (props.message.attachment) {
    image = props.message.attachment;
  }

  return (
    <div
      id={props.latest ? "latest" : null}
      className={styles.bubble}
      style={{
        backgroundColor: props.isSender ? "#05f" : "#0cf",
        float: props.isSender ? "left" : "right"
      }}
      id={`${props.MessageID}`}
    >
      {props.showSender && !props.isSender ? (
        <p>{props.message.sender.username}</p>
      ) : null}

      <p>
        {props.message.message_text}
        <br />
        <span
          style={{
            float: "right",
            color: "#ddd"
          }}
        >
          {props.created}
        </span>
      </p>
      <div
        style={{
          display: "flex",
          width: "100%",
          padding: " 5px",
          justifyContent: "center"
        }}
      >
        {image ? (
          <a href={props.message.attachment}>
            <img
              style={{ display: "inline-block" }}
              width={250}
              height={150}
              src={props.message.attachment}
            />
          </a>
        ) : props.message.attachment ? (
          <a href={props.message.attachment}>
            <i
              className="fas fa-file"
              style={{ display: "inline-block", fontSize: "6rem" }}
            />
          </a>
        ) : null}
      </div>
    </div>
  );
};

export default MessageBubble;
