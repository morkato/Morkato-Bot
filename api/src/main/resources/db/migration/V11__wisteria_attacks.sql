ALTER TABLE "attacks"
  ADD COLUMN "wisteria" attr_type
    NOT NULL
    DEFAULT 0
;
ALTER TABLE "attacks"
  ADD COLUMN "wisteria_turn" attr_type
    NOT NULL
    DEFAULT 0
;