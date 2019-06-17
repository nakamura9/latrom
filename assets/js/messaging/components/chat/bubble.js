import React from "react";
import styles from "./chatStyles.css";

const MessageBubble = props => {
  let isImage;
  const isSelected = props.selectedMessages.includes(props.message.id);

  if (props.message.attachment) {
    isImage = ["png", "jpg", "jpeg", "gif"].includes(
      props.message.attachment.split(".")[1]
    );
  }

  return (
      <div
        id={props.latest ? "latest" : null}
        className={styles.bubble}
        style={{
          backgroundColor: props.isSender ? "#05f" : "#0cf",
          float: props.isSender ? "left" : "right",
          border: isSelected ? '5px solid #aaa': null
        }}
        id={`${props.MessageID}`}
        onClick={() => {
          if (!props.canBeSelected) {
            return;
          }
          props.selectHandler(props.message.id);
        }}
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
          {isImage ? (
            <a
              href={props.message.attachment}
              style={{ color: "white", textDecoration: "none" }}
              download
              target="_blank"
            >
              <img
                style={{ display: "inline-block" }}
                width={250}
                height={150}
                src={props.message.attachment}
              />
            </a>
          ) : props.message.attachment ? (
            <a
              href={props.message.attachment}
              style={{ color: "white", textDecoration: "none" }}
              download
              target="_blank"
            >
              <i
                className="fas fa-file"
                style={{
                  display: "inline-block",
                  fontSize: "6rem",
                  color: "white"
                }}
              />
            </a>
          ) : null}
        </div>
      </div>
  );
};

export default MessageBubble;
